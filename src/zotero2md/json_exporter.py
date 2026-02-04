import os
import json
from typing import Dict, Any, List
from zotero2md.logger import get_logger


class JSONExporter:
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def export_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            export_data = {
                'key': item_data.get('key', ''),
                'type': item_data.get('type', ''),
                'title': item_data.get('title', ''),
                'authors': item_data.get('authors', []),
                'date': item_data.get('date', ''),
                'publication': item_data.get('publication', ''),
                'doi': item_data.get('doi', ''),
                'url': item_data.get('url', ''),
                'abstract': item_data.get('abstract', ''),
                'tags': item_data.get('tags', []),
                'notes': item_data.get('notes', []),
                'attachments': item_data.get('attachments', []),
                'collections': item_data.get('collections', [])
            }
            
            self.logger.debug(f"生成 JSON 条目: {item_data.get('key', 'unknown')}")
            return export_data
        except Exception as e:
            self.logger.error(f"生成 JSON 条目失败: {e}", exc_info=True)
            return None
    
    def export_items(self, items: List[Dict[str, Any]], output_path: str, indent: int = 2) -> Dict[str, int]:
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            success_count = 0
            failed_count = 0
            export_data = []
            
            for item in items:
                item_json = self.export_item(item)
                if item_json:
                    export_data.append(item_json)
                    success_count += 1
                else:
                    failed_count += 1
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=indent)
            
            self.logger.info(f"JSON 导出完成: 成功 {success_count}, 失败 {failed_count}")
            return {'success': success_count, 'failed': failed_count}
        except Exception as e:
            self.logger.error(f"JSON 导出失败: {e}", exc_info=True)
            return {'success': 0, 'failed': len(items)}