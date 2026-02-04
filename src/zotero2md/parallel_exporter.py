import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from zotero2md.logger import get_logger


class ParallelExporter:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.logger = get_logger(__name__)
    
    def export_items_parallel(
        self,
        items: List[Dict[str, Any]],
        export_func,
        progress_callback=None
    ) -> Dict[str, Any]:
        results = {
            'success': 0,
            'skipped': 0,
            'error': 0,
            'errors': []
        }
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(export_func, item): item
                for item in items
            }
            
            for i, future in enumerate(as_completed(futures)):
                try:
                    item = futures[future]
                    result = future.result()
                    
                    if result:
                        results['success'] += 1
                        self.logger.debug(f"已导出: {item.get('title', 'Unknown')}")
                    else:
                        results['skipped'] += 1
                        self.logger.debug(f"已跳过: {item.get('title', 'Unknown')}")
                    
                    if progress_callback:
                        progress_callback(i + 1, len(items))
                        
                except Exception as e:
                    results['error'] += 1
                    error_info = {
                        'item': item,
                        'error': str(e)
                    }
                    results['errors'].append(error_info)
                    self.logger.error(f"导出条目 {item.get('key', 'Unknown')} 失败: {e}", exc_info=True)
                    
                    if progress_callback:
                        progress_callback(i + 1, len(items))
        
        return results
    
    def export_items_with_progress(
        self,
        items: List[Dict[str, Any]],
        export_func,
        batch_size: int = 10
    ) -> Dict[str, Any]:
        results = {
            'success': 0,
            'skipped': 0,
            'error': 0,
            'errors': []
        }
        
        total_items = len(items)
        self.logger.info(f"开始并行导出 {total_items} 个条目，使用 {self.max_workers} 个工作线程")
        
        def progress_callback(current: int, total: int):
            percentage = (current / total) * 100
            bar_length = 40
            filled = int(bar_length * current / total)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r[*] 进度: [{bar}] {percentage:.1f}% ({current}/{total})", end="", flush=True)
        
        results = self.export_items_parallel(items, export_func, progress_callback)
        
        print(f"\n[*] 并行导出完成！成功: {results['success']}, 跳过: {results['skipped']}, 失败: {results['error']}")
        
        return results
