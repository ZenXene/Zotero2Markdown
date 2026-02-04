import os
from typing import Dict, Any, List, Optional
from zotero2md.logger import get_logger


class BibTeXExporter:
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def escape_bibtex(self, text: str) -> str:
        if not text:
            return ""
        text = text.replace('&', '\\&')
        text = text.replace('%', '\\%')
        text = text.replace('$', '\\$')
        text = text.replace('#', '\\#')
        text = text.replace('_', '\\_')
        text = text.replace('{', '\\{')
        text = text.replace('}', '\\}')
        text = text.replace('~', '\\~')
        text = text.replace('^', '\\^')
        text = text.replace('"', '"')
        return text
    
    def get_bibtex_type(self, zotero_type: str) -> str:
        type_mapping = {
            'journalArticle': 'article',
            'book': 'book',
            'bookSection': 'inbook',
            'conferencePaper': 'inproceedings',
            'magazineArticle': 'article',
            'newspaperArticle': 'article',
            'webpage': 'misc',
            'thesis': 'phdthesis',
            'report': 'techreport',
            'preprint': 'misc',
            'blogPost': 'misc',
            'forumPost': 'misc',
            'podcast': 'misc',
            'presentation': 'misc',
            'videoRecording': 'misc',
            'case': 'misc',
            'statute': 'misc',
            'patent': 'patent',
            'email': 'misc',
            'map': 'misc',
            'dictionaryEntry': 'misc',
            'encyclopediaArticle': 'misc',
            'document': 'misc'
        }
        return type_mapping.get(zotero_type, 'misc')
    
    def format_authors(self, authors: List[str]) -> str:
        if not authors:
            return ""
        return " and ".join(authors)
    
    def export_item(self, item_data: Dict[str, Any]) -> Optional[str]:
        try:
            bibtex_type = self.get_bibtex_type(item_data.get('type', 'misc'))
            key = item_data.get('key', 'unknown')
            
            fields = []
            
            title = self.escape_bibtex(item_data.get('title', ''))
            if title:
                fields.append(f"  title = {{{title}}}")
            
            authors = self.format_authors(item_data.get('authors', []))
            if authors:
                fields.append(f"  author = {{{authors}}}")
            
            date = item_data.get('date', '')
            if date:
                year = date.split('-')[0] if '-' in date else date
                if year and year.isdigit():
                    fields.append(f"  year = {{{year}}}")
            
            publication = self.escape_bibtex(item_data.get('publication', ''))
            if publication:
                if bibtex_type == 'article':
                    fields.append(f"  journal = {{{publication}}}")
                elif bibtex_type == 'inproceedings':
                    fields.append(f"  booktitle = {{{publication}}}")
                elif bibtex_type == 'book':
                    fields.append(f"  publisher = {{{publication}}}")
                else:
                    fields.append(f"  publisher = {{{publication}}}")
            
            doi = item_data.get('doi', '')
            if doi:
                fields.append(f"  doi = {{{doi}}}")
            
            url = item_data.get('url', '')
            if url:
                fields.append(f"  url = {{{url}}}")
            
            abstract = self.escape_bibtex(item_data.get('abstract', ''))
            if abstract:
                fields.append(f"  abstract = {{{abstract}}}")
            
            tags = item_data.get('tags', [])
            if tags:
                keywords = ", ".join(tags)
                fields.append(f"  keywords = {{{keywords}}}")
            
            bibtex_entry = f"@{bibtex_type}{{{key},\n"
            bibtex_entry += ",\n".join(fields)
            bibtex_entry += "\n}\n"
            
            self.logger.debug(f"生成 BibTeX 条目: {key}")
            return bibtex_entry
        except Exception as e:
            self.logger.error(f"生成 BibTeX 条目失败: {e}", exc_info=True)
            return None
    
    def export_items(self, items: List[Dict[str, Any]], output_path: str) -> Dict[str, int]:
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            success_count = 0
            failed_count = 0
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for item in items:
                    bibtex_entry = self.export_item(item)
                    if bibtex_entry:
                        f.write(bibtex_entry)
                        success_count += 1
                    else:
                        failed_count += 1
            
            self.logger.info(f"BibTeX 导出完成: 成功 {success_count}, 失败 {failed_count}")
            return {'success': success_count, 'failed': failed_count}
        except Exception as e:
            self.logger.error(f"BibTeX 导出失败: {e}", exc_info=True)
            return {'success': 0, 'failed': len(items)}