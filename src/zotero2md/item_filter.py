import re
from typing import List, Dict, Any
from zotero2md.logger import get_logger


class ItemFilter:
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def filter_by_regex(
        self,
        items: List[Dict[str, Any]],
        title_pattern: str = None,
        author_pattern: str = None,
        abstract_pattern: str = None
    ) -> List[Dict[str, Any]]:
        filtered_items = []
        
        for item in items:
            match = True
            
            if title_pattern:
                if not self._match_pattern(item.get('title', ''), title_pattern):
                    match = False
            
            if match and author_pattern:
                authors = item.get('authors', [])
                author_text = ', '.join([a.get('name', '') for a in authors])
                if not self._match_pattern(author_text, author_pattern):
                    match = False
            
            if match and abstract_pattern:
                abstract = item.get('abstract', '')
                if not self._match_pattern(abstract, abstract_pattern):
                    match = False
            
            if match:
                filtered_items.append(item)
                self.logger.debug(f"条目匹配: {item.get('title', 'Unknown')}")
            else:
                self.logger.debug(f"条目被过滤: {item.get('title', 'Unknown')}")
        
        self.logger.info(f"正则过滤: {len(items)} -> {len(filtered_items)}")
        return filtered_items
    
    def _match_pattern(self, text: str, pattern: str) -> bool:
        try:
            return bool(re.search(pattern, text, re.IGNORECASE))
        except re.error as e:
            self.logger.error(f"正则表达式错误: {pattern}, {e}")
            return False
    
    def filter_by_date_range(
        self,
        items: List[Dict[str, Any]],
        start_year: int = None,
        end_year: int = None
    ) -> List[Dict[str, Any]]:
        if start_year is None and end_year is None:
            return items
        
        filtered_items = []
        
        for item in items:
            date = item.get('date', '')
            if not date:
                continue
            
            year = self._extract_year(date)
            if year is None:
                continue
            
            if start_year and year < start_year:
                continue
            
            if end_year and year > end_year:
                continue
            
            filtered_items.append(item)
        
        self.logger.info(f"日期范围过滤: {len(items)} -> {len(filtered_items)}")
        return filtered_items
    
    def _extract_year(self, date: str) -> int:
        year_match = re.search(r'\b(19|20)\d{2}\b', date)
        if year_match:
            return int(year_match.group(1))
        return None
    
    def filter_by_tags(
        self,
        items: List[Dict[str, Any]],
        include_tags: List[str] = None,
        exclude_tags: List[str] = None,
        match_all: bool = False
    ) -> List[Dict[str, Any]]:
        if not include_tags and not exclude_tags:
            return items
        
        filtered_items = []
        
        for item in items:
            item_tags = [tag.lower() for tag in item.get('tags', [])]
            include_tags_lower = [tag.lower() for tag in (include_tags or [])]
            exclude_tags_lower = [tag.lower() for tag in (exclude_tags or [])]
            
            match = True
            
            if include_tags_lower:
                if match_all:
                    match = all(tag in item_tags for tag in include_tags_lower)
                else:
                    match = any(tag in item_tags for tag in include_tags_lower)
            
            if match and exclude_tags_lower:
                match = not any(tag in item_tags for tag in exclude_tags_lower)
            
            if match:
                filtered_items.append(item)
                self.logger.debug(f"条目匹配标签: {item.get('title', 'Unknown')}")
            else:
                self.logger.debug(f"条目被标签过滤: {item.get('title', 'Unknown')}")
        
        self.logger.info(f"标签过滤: {len(items)} -> {len(filtered_items)}")
        return filtered_items
    
    def filter_by_collections(
        self,
        items: List[Dict[str, Any]],
        include_collections: List[str] = None,
        exclude_collections: List[str] = None
    ) -> List[Dict[str, Any]]:
        if not include_collections and not exclude_collections:
            return items
        
        filtered_items = []
        
        for item in items:
            item_collections = [col.lower() for col in item.get('collections', [])]
            include_collections_lower = [col.lower() for col in (include_collections or [])]
            exclude_collections_lower = [col.lower() for col in (exclude_collections or [])]
            
            match = True
            
            if include_collections_lower:
                match = any(col in item_collections for col in include_collections_lower)
            
            if match and exclude_collections_lower:
                match = not any(col in item_collections for col in exclude_collections_lower)
            
            if match:
                filtered_items.append(item)
                self.logger.debug(f"条目匹配收藏夹: {item.get('title', 'Unknown')}")
            else:
                self.logger.debug(f"条目被收藏夹过滤: {item.get('title', 'Unknown')}")
        
        self.logger.info(f"收藏夹过滤: {len(items)} -> {len(filtered_items)}")
        return filtered_items
    
    def filter_by_custom_fields(
        self,
        items: List[Dict[str, Any]],
        field_filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        if not field_filters:
            return items
        
        filtered_items = []
        
        for item in items:
            metadata = item.get('metadata', {})
            match = True
            
            for field_name, field_value in field_filters.items():
                item_value = metadata.get(field_name, '')
                
                if isinstance(field_value, str):
                    if field_value not in item_value:
                        match = False
                        break
                elif isinstance(field_value, dict):
                    pattern = field_value.get('pattern')
                    regex = field_value.get('regex', False)
                    
                    if regex:
                        if not self._match_pattern(item_value, pattern):
                            match = False
                            break
                    else:
                        if pattern not in item_value:
                            match = False
                            break
                else:
                    if item_value != field_value:
                        match = False
                        break
            
            if match:
                filtered_items.append(item)
                self.logger.debug(f"条目匹配自定义字段: {item.get('title', 'Unknown')}")
            else:
                self.logger.debug(f"条目被自定义字段过滤: {item.get('title', 'Unknown')}")
        
        self.logger.info(f"自定义字段过滤: {len(items)} -> {len(filtered_items)}")
        return filtered_items
