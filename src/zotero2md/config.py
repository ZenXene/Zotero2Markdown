import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self.find_config_file()
        self.config = self.load_config()
    
    @staticmethod
    def find_config_file() -> Optional[str]:
        possible_paths = [
            'zotero2md.yml',
            'zotero2md.yaml',
            'config.yml',
            'config.yaml',
            Path.home() / '.zotero2md.yml',
            Path.home() / '.zotero2md.yaml'
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return str(path)
        return None
    
    def load_config(self) -> Dict[str, Any]:
        default_config = {
            'database': {
                'path': None,
                'auto_detect': True
            },
            'output': {
                'directory': 'output',
                'filename_format': '{title}',
                'sanitize_filename': True,
                'max_filename_length': 200
            },
            'export': {
                'template': 'default.md',
                'template_dir': 'templates',
                'include_attachments': False,
                'attachment_path_type': 'relative',
                'convert_html_notes': True
            },
            'filters': {
                'item_types': [],
                'tags': [],
                'exclude_tags': [],
                'collections': []
            },
            'advanced': {
                'incremental_update': False,
                'overwrite_existing': True,
                'batch_size': 50,
                'log_file': None
            }
        }
        
        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
                    self._merge_config(default_config, user_config)
            except Exception as e:
                print(f"警告: 无法加载配置文件 {self.config_path}: {e}")
        
        return default_config
    
    def _merge_config(self, base: Dict, override: Dict):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key_path: str, default=None):
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def save_default_config(self, output_path: str = 'zotero2md.yml'):
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
        print(f"默认配置已保存到: {output_path}")
