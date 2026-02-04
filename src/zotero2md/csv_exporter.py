import os
import csv
from typing import Dict, Any, List
from zotero2md.logger import get_logger


class CSVExporter:
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def escape_csv(self, text: str) -> str:
        if not text:
            return ""
        text = text.replace('"', '""')
        return f'"{text}"'
    
    def export_item(self, item_data: Dict[str, Any]) -> Dict[str, str]:
        try:
            export_data = {
                'Key': item_data.get('key', ''),
                'Type': item_data.get('type', ''),
                'Title': item_data.get('title', ''),
                'Authors': ', '.join(item_data.get('authors', [])),
                'Date': item_data.get('date', ''),
                'Publication': item_data.get('publication', ''),
                'DOI': item_data.get('doi', ''),
                'URL': item_data.get('url', ''),
                'Abstract': item_data.get('abstract', ''),
                'Tags': ', '.join(item_data.get('tags', [])),
                'Collections': ', '.join(item_data.get('collections', []))
            }
            
            self.logger.debug(f"生成 CSV 条目: {item_data.get('key', 'unknown')}")
            return export_data
        except Exception as e:
            self.logger.error(f"生成 CSV 条目失败: {e}", exc_info=True)
            return None
    
    def export_items(self, items: List[Dict[str, Any]], output_path: str) -> Dict[str, int]:
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            success_count = 0
            failed_count = 0
            
            fieldnames = ['Key', 'Type', 'Title', 'Authors', 'Date', 'Publication', 'DOI', 'URL', 'Abstract', 'Tags', 'Collections']
            
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in items:
                    item_csv = self.export_item(item)
                    if item_csv:
                        writer.writerow(item_csv)
                        success_count += 1
                    else:
                        failed_count += 1
            
            self.logger.info(f"CSV 导出完成: 成功 {success_count}, 失败 {failed_count}")
            return {'success': success_count, 'failed': failed_count}
        except Exception as e:
            self.logger.error(f"CSV 导出失败: {e}", exc_info=True)
            return {'success': 0, 'failed': len(items)}