import unittest
import tempfile
import os
from zotero2md.bibtex_exporter import BibTeXExporter


class TestBibTeXExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = BibTeXExporter()
    
    def test_escape_bibtex(self):
        self.assertEqual(self.exporter.escape_bibtex('Test & String'), 'Test \\& String')
        self.assertEqual(self.exporter.escape_bibtex('Test % String'), 'Test \\% String')
        self.assertEqual(self.exporter.escape_bibtex('Test $ String'), 'Test \\$ String')
        self.assertEqual(self.exporter.escape_bibtex(''), '')
        self.assertEqual(self.exporter.escape_bibtex(None), '')
    
    def test_get_bibtex_type(self):
        self.assertEqual(self.exporter.get_bibtex_type('journalArticle'), 'article')
        self.assertEqual(self.exporter.get_bibtex_type('book'), 'book')
        self.assertEqual(self.exporter.get_bibtex_type('conferencePaper'), 'inproceedings')
        self.assertEqual(self.exporter.get_bibtex_type('thesis'), 'phdthesis')
        self.assertEqual(self.exporter.get_bibtex_type('unknownType'), 'misc')
    
    def test_format_authors(self):
        authors = ['Author One', 'Author Two', 'Author Three']
        result = self.exporter.format_authors(authors)
        self.assertEqual(result, 'Author One and Author Two and Author Three')
        
        self.assertEqual(self.exporter.format_authors([]), '')
        self.assertEqual(self.exporter.format_authors(['Single Author']), 'Single Author')
    
    def test_export_item(self):
        item_data = {
            'key': 'TEST123',
            'type': 'journalArticle',
            'title': 'Test Article Title',
            'authors': ['Author One', 'Author Two'],
            'date': '2023-01-01',
            'publication': 'Test Journal',
            'doi': '10.1234/test',
            'url': 'https://example.com',
            'abstract': 'Test abstract',
            'tags': ['tag1', 'tag2']
        }
        
        result = self.exporter.export_item(item_data)
        
        self.assertIsNotNone(result)
        self.assertIn('@article{TEST123', result)
        self.assertIn('title = {Test Article Title}', result)
        self.assertIn('author = {Author One and Author Two}', result)
        self.assertIn('year = {2023}', result)
        self.assertIn('journal = {Test Journal}', result)
        self.assertIn('doi = {10.1234/test}', result)
        self.assertIn('keywords = {tag1, tag2}', result)
    
    def test_export_items(self):
        items = [
            {
                'key': 'TEST1',
                'type': 'journalArticle',
                'title': 'Article 1',
                'authors': ['Author 1'],
                'date': '2023',
                'publication': 'Journal 1',
                'doi': '10.1234/1',
                'url': '',
                'abstract': '',
                'tags': []
            },
            {
                'key': 'TEST2',
                'type': 'book',
                'title': 'Book 1',
                'authors': ['Author 2'],
                'date': '2022',
                'publication': 'Publisher 1',
                'doi': '',
                'url': '',
                'abstract': '',
                'tags': []
            }
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test.bib')
            result = self.exporter.export_items(items, output_path)
            
            self.assertEqual(result['success'], 2)
            self.assertEqual(result['failed'], 0)
            self.assertTrue(os.path.exists(output_path))
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('@article{TEST1', content)
                self.assertIn('@book{TEST2', content)


if __name__ == '__main__':
    unittest.main()