import logging
from typing import Dict, Any, Optional
from zotero2md.logger import get_logger


class QueryCache:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, Any] = {}
        self.logger = get_logger(__name__)
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            self.logger.debug(f"缓存命中: {key}")
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        if len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.logger.debug(f"缓存已满，删除最旧项: {oldest_key}")
        
        self.cache[key] = value
        self.logger.debug(f"缓存添加: {key}")
    
    def clear(self) -> None:
        self.cache.clear()
        self.logger.info("缓存已清空")
    
    def get_stats(self) -> Dict[str, int]:
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_rate': 0.0
        }
