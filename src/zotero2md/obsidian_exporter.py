import os
from typing import Dict, Any, List, Optional
from zotero2md.logger import get_logger


class ObsidianExporter:
    def __init__(self, vault_path: str, notes_folder: str = "Zotero"):
        self.vault_path = vault_path
        self.notes_folder = notes_folder
        self.output_dir = os.path.join(vault_path, notes_folder)
        self.logger = get_logger(__name__)
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def export_item(self, item_data: Dict[str, Any]) -> Optional[str]:
        try:
            filename = self._sanitize_filename(item_data.get('title', 'Untitled'))
            filepath = os.path.join(self.output_dir, f"{filename}.md")
            
            content = self._convert_to_obsidian_format(item_data)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"成功导出到 Obsidian: {item_data.get('title', 'Unknown')}")
            return filepath
        except Exception as e:
            self.logger.error(f"导出到 Obsidian 失败: {e}", exc_info=True)
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename[:200]
    
    def _convert_to_obsidian_format(self, item_data: Dict[str, Any]) -> str:
        lines = []
        
        lines.append("---")
        lines.append(f"title: {item_data.get('title', 'Untitled')}")
        lines.append(f"authors: {', '.join(item_data.get('authors', []))}")
        lines.append(f"date: {item_data.get('date', 'Unknown')}")
        lines.append(f"type: {item_data.get('type', 'unknown')}")
        
        if item_data.get('doi'):
            lines.append(f"doi: {item_data['doi']}")
        
        if item_data.get('url'):
            lines.append(f"url: {item_data['url']}")
        
        if item_data.get('publication'):
            lines.append(f"publication: {item_data['publication']}")
        
        tags = item_data.get('tags', [])
        if tags:
            lines.append(f"tags: {', '.join(tags)}")
        
        collections = item_data.get('collections', [])
        if collections:
            lines.append(f"collections: {', '.join(collections)}")
        
        lines.append("---")
        lines.append("")
        
        lines.append(f"# {item_data.get('title', 'Untitled')}")
        lines.append("")
        
        if item_data.get('authors'):
            lines.append(f"**Authors:** {', '.join(item_data['authors'])}")
            lines.append("")
        
        if item_data.get('date'):
            lines.append(f"**Date:** {item_data['date']}")
            lines.append("")
        
        if item_data.get('publication'):
            lines.append(f"**Publication:** {item_data['publication']}")
            lines.append("")
        
        if item_data.get('doi'):
            lines.append(f"**DOI:** [{item_data['doi']}](https://doi.org/{item_data['doi']})")
            lines.append("")
        
        if item_data.get('url'):
            lines.append(f"**URL:** [{item_data['url']}]({item_data['url']})")
            lines.append("")
        
        if item_data.get('abstract'):
            lines.append("## Abstract")
            lines.append("")
            lines.append(item_data['abstract'])
            lines.append("")
        
        if item_data.get('notes'):
            lines.append("## Notes")
            lines.append("")
            for note in item_data['notes']:
                lines.append(note)
                lines.append("")
        
        if item_data.get('attachments'):
            lines.append("## Attachments")
            lines.append("")
            for attachment in item_data['attachments']:
                path = attachment.get('path', '')
                if path:
                    lines.append(f"- [[{path}]]")
            lines.append("")
        
        return '\n'.join(lines)
    
    def export_items_batch(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        results = {
            'success': 0,
            'failed': 0,
            'filepaths': []
        }
        
        for item in items:
            filepath = self.export_item(item)
            if filepath:
                results['success'] += 1
                results['filepaths'].append(filepath)
            else:
                results['failed'] += 1
        
        self.logger.info(f"批量导出完成: 成功 {results['success']}, 失败 {results['failed']}")
        return results