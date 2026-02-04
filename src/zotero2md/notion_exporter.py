import requests
import json
from typing import Dict, Any, List, Optional
from zotero2md.logger import get_logger


class NotionExporter:
    def __init__(self, api_key: str, database_id: str):
        self.api_key = api_key
        self.database_id = database_id
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.logger = get_logger(__name__)
    
    def export_item(self, item_data: Dict[str, Any]) -> Optional[str]:
        try:
            page_data = self._convert_to_notion_format(item_data)
            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=page_data
            )
            
            if response.status_code == 200:
                page_id = response.json().get('id')
                self.logger.info(f"成功导出到 Notion: {item_data.get('title', 'Unknown')}")
                return page_id
            else:
                self.logger.error(f"Notion API 错误: {response.status_code}, {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"导出到 Notion 失败: {e}", exc_info=True)
            return None
    
    def _convert_to_notion_format(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        properties = {
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": item_data.get('title', 'Untitled')
                        }
                    }
                ]
            },
            "Authors": {
                "multi_select": [{"name": author} for author in item_data.get('authors', [])]
            },
            "Date": {
                "date": {
                    "start": item_data.get('date', '')
                }
            },
            "Type": {
                "select": {
                    "name": item_data.get('type', 'unknown')
                }
            },
            "DOI": {
                "url": item_data.get('doi', '')
            },
            "URL": {
                "url": item_data.get('url', '')
            },
            "Tags": {
                "multi_select": [{"name": tag} for tag in item_data.get('tags', [])]
            },
            "Publication": {
                "rich_text": [
                    {
                        "text": {
                            "content": item_data.get('publication', '')
                        }
                    }
                ]
            }
        }
        
        blocks = []
        
        if item_data.get('abstract'):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Abstract"}}]
                }
            })
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": item_data['abstract']}}]
                }
            })
        
        if item_data.get('notes'):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Notes"}}]
                }
            })
            for note in item_data['notes']:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": note}}]
                    }
                })
        
        if item_data.get('attachments'):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Attachments"}}]
                }
            })
            for attachment in item_data['attachments']:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": attachment.get('path', '')}}]
                    }
                })
        
        return {
            "parent": {"database_id": self.database_id},
            "properties": properties,
            "children": blocks
        }
    
    def export_items_batch(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        results = {
            'success': 0,
            'failed': 0,
            'page_ids': []
        }
        
        for item in items:
            page_id = self.export_item(item)
            if page_id:
                results['success'] += 1
                results['page_ids'].append(page_id)
            else:
                results['failed'] += 1
        
        self.logger.info(f"批量导出完成: 成功 {results['success']}, 失败 {results['failed']}")
        return results