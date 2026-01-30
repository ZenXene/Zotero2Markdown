import os
import hashlib
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, Optional

class MarkdownExporter:
    def __init__(self, template_dir='templates', template_name='default.md', config=None):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.env.get_template(template_name)
        self.config = config
        self.exported_files = {}

    def sanitize_filename(self, title: str, max_length: int = 200) -> str:
        safe_chars = " -_.,()[]{}"
        safe_title = "".join([c for c in title if c.isalnum() or c in safe_chars]).strip()
        safe_title = safe_title.replace(' ', '_')
        
        if len(safe_title) > max_length:
            safe_title = safe_title[:max_length].rstrip('_')
        
        return safe_title or 'untitled'

    def generate_filename(self, item_data: Dict[str, Any]) -> str:
        if self.config:
            filename_format = self.config.get('output.filename_format', '{title}')
            max_length = self.config.get('output.max_filename_length', 200)
        else:
            filename_format = '{title}'
            max_length = 200
        
        try:
            filename = filename_format.format(**item_data)
        except KeyError:
            filename = item_data.get('title', 'untitled')
        
        if self.config and self.config.get('output.sanitize_filename', True):
            filename = self.sanitize_filename(filename, max_length)
        
        return f"{filename}.md"

    def render(self, item_data: Dict[str, Any]) -> str:
        try:
            return self.template.render(**item_data)
        except Exception as e:
            error_msg = f"模板渲染失败: {e}\n数据: {item_data}"
            return f"<!-- {error_msg} -->\n\n# {item_data.get('title', 'Error')}\n\n渲染失败，请检查模板。"

    def get_file_hash(self, file_path: Path) -> Optional[str]:
        if not file_path.exists():
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def should_export(self, file_path: Path, content: str) -> bool:
        if not self.config:
            return True
        
        overwrite = self.config.get('advanced.overwrite_existing', True)
        incremental = self.config.get('advanced.incremental_update', False)
        
        if not file_path.exists():
            return True
        
        if overwrite:
            return True
        
        if incremental:
            existing_hash = self.get_file_hash(file_path)
            new_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            return existing_hash != new_hash
        
        return False

    def export(self, item_data: Dict[str, Any], output_dir='output') -> Optional[Path]:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        filename = self.generate_filename(item_data)
        file_path = output_path / filename
        
        content = self.render(item_data)
        
        if not self.should_export(file_path, content):
            return None
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.exported_files[item_data.get('key', '')] = str(file_path)
        return file_path

    def get_export_summary(self) -> Dict[str, int]:
        return {
            'total': len(self.exported_files),
            'files': list(self.exported_files.values())
        }

if __name__ == "__main__":
    from zotero2md.database import ZoteroConnector
    from zotero2md.parser import ZoteroParser
    
    connector = ZoteroConnector()
    conn = connector.connect()
    if conn:
        parser = ZoteroParser(conn)
        items = parser.get_all_items()
        
        if items:
            item = items[0]
            metadata = parser.get_item_metadata(item['itemID'])
            creators = parser.get_item_creators(item['itemID'])
            tags = parser.get_item_tags(item['itemID'])
            notes = parser.get_item_notes(item['itemID'])
            attachments = parser.get_item_attachments(item['itemID'])
            collections = parser.get_item_collections(item['itemID'])
            
            item_data = {
                'title': metadata.get('title', 'Untitled'),
                'authors': [c['name'] for c in creators],
                'date': metadata.get('date', 'Unknown'),
                'type': item['typeName'],
                'doi': metadata.get('DOI', ''),
                'url': metadata.get('url', ''),
                'tags': tags,
                'key': item['key'],
                'publication': metadata.get('publicationTitle', ''),
                'abstract': metadata.get('abstractNote', ''),
                'notes': notes,
                'attachments': attachments,
                'collections': collections
            }
            
            exporter = MarkdownExporter()
            saved_path = exporter.export(item_data)
            print(f"成功导出条目到: {saved_path}")
            
        connector.close()
