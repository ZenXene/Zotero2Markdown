import unittest
import tempfile
import os
import json
from zotero2md.json_exporter import JSONExporter


class TestJSONExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = JSONExporter()
    
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
            'notes': ['Note 1', 'Note 2'],
            'attachments': ['file1.pdf'],
            'collections': ['Collection 1']
        }
        
        result = self.exporter.export_item(item_data)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['key'], 'TEST123')
        self.assertEqual(result['type'], 'journalArticle')
        self.assertEqual(result['title'], 'Test Article Title')
        self.assertEqual(result['authors'], ['Author One', 'Author Two'])
        self.assertEqual(result['date'], '2023-01-01')
        self.assertEqual(result['publication'], 'Test Journal')
        self.assertEqual(result['doi'], '10.1234/test')
        self.assertEqual(result['url'], 'https://example.com')
        self.assertEqual(result['abstract'], 'Test abstract')
        self.assertEqual(result['tags'], ['tag1', 'tag2'])
        self.assertEqual(result['notes'], ['Note 1', 'Note 2'])
        self.assertEqual(result['attachments'], ['file1.pdf'])
        self.assertEqual(result['collections'], ['Collection 1'])
    
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
                'notes': [],
                'attachments': [],
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
                'notes': [],
                'attachments': [],
                'collections': []
            }
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test.json')
            result = self.exporter.export_items(items, output_path, indent=2)
            
            self.assertEqual(result['success'], 2)
            self.assertEqual(result['failed'], 0)
            self.assertTrue(os.path.exists(output_path))
            
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.assertEqual(len(data), 2)
                self.assertEqual(data[0]['key'], 'TEST1')
                self.assertEqual(data[1]['key'], 'TEST2')
    
    def test_export_items_with_custom_indent(self):
        items = [
            {
                'key': 'TEST1',
                'type': 'journalArticle',
                'title': 'Article 1',
                'authors': ['Author 1'],
                'date': '2023',
                'publication': 'Journal 1',
                'doi': '',
                'url': '',
                'abstract': '',
                'tags': [],
                'notes': [],
                'attachments': [],
                'collections': []
            }
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_indent.json')
            result = self.exporter.export_items(items, output_path, indent=4)
            
            self.assertEqual(result['success'], 1)
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('    "key":', content)


if __name__ == '__main__':
    unittest.main()