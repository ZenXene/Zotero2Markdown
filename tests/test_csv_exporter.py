import unittest
import tempfile
import os
import csv
from zotero2md.csv_exporter import CSVExporter


class TestCSVExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = CSVExporter()
    
    def test_escape_csv(self):
        self.assertEqual(self.exporter.escape_csv('Test "String"'), '"Test ""String"""')
        self.assertEqual(self.exporter.escape_csv(''), '')
        self.assertEqual(self.exporter.escape_csv(None), '')
    
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
            'tags': ['tag1', 'tag2'],
            'collections': ['Collection 1']
        }
        
        result = self.exporter.export_item(item_data)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['Key'], 'TEST123')
        self.assertEqual(result['Type'], 'journalArticle')
        self.assertEqual(result['Title'], 'Test Article Title')
        self.assertEqual(result['Authors'], 'Author One, Author Two')
        self.assertEqual(result['Date'], '2023-01-01')
        self.assertEqual(result['Publication'], 'Test Journal')
        self.assertEqual(result['DOI'], '10.1234/test')
        self.assertEqual(result['URL'], 'https://example.com')
        self.assertEqual(result['Abstract'], 'Test abstract')
        self.assertEqual(result['Tags'], 'tag1, tag2')
        self.assertEqual(result['Collections'], 'Collection 1')
    
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
                'tags': [],
                'collections': []
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
                'tags': [],
                'collections': []
            }
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test.csv')
            result = self.exporter.export_items(items, output_path)
            
            self.assertEqual(result['success'], 2)
            self.assertEqual(result['failed'], 0)
            self.assertTrue(os.path.exists(output_path))
            
            with open(output_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[0]['Key'], 'TEST1')
                self.assertEqual(rows[1]['Key'], 'TEST2')


if __name__ == '__main__':
    unittest.main()