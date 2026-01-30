import sqlite3
import os
import platform
import shutil
import tempfile
from pathlib import Path

class ZoteroConnector:
    """Zotero 本地数据库连接器"""
    
    def __init__(self, database_path=None):
        self.database_path = database_path or self.find_zotero_db()
        if not self.database_path:
            raise FileNotFoundError("无法找到 Zotero 数据库文件。请手动指定路径。")
        self.conn = None
        self.temp_db = None

    @staticmethod
    def find_zotero_db():
        """尝试查找 Zotero 数据库的默认路径"""
        system = platform.system()
        home = Path.home()
        
        paths = []
        if system == "Darwin":  # macOS
            paths.append(home / "Library/Application Support/Zotero/Profiles")
            paths.append(home / "Zotero")
        elif system == "Windows":
            paths.append(Path(os.environ.get("APPDATA", "")) / "Zotero/Zotero/Profiles")
        elif system == "Linux":
            paths.append(home / ".zotero/zotero")

        for p in paths:
            if p.exists():
                # 检查是否直接在目录下
                db_path = p / "zotero.sqlite"
                if db_path.exists():
                    return str(db_path)
                
                # 检查 Profile 模式
                for profile in p.glob("*.default*"):
                    db_path = profile / "zotero.sqlite"
                    if db_path.exists():
                        return str(db_path)
        
        # 兜底检查当前目录下是否有 zotero.sqlite
        if Path("zotero.sqlite").exists():
            return str(Path("zotero.sqlite").absolute())
            
        return None

    def connect(self):
        """建立连接（通过临时副本以避免数据库锁定）"""
        try:
            # 创建临时文件
            fd, self.temp_db = tempfile.mkstemp(suffix=".sqlite")
            os.close(fd)
            
            # 复制数据库文件
            shutil.copy2(self.database_path, self.temp_db)
            
            # 连接到临时数据库
            self.conn = sqlite3.connect(self.temp_db)
            self.conn.row_factory = sqlite3.Row
            return self.conn
        except Exception as e:
            print(f"连接 Zotero 数据库失败: {e}")
            self.cleanup()
            return None

    def cleanup(self):
        """清理临时文件"""
        if self.temp_db and os.path.exists(self.temp_db):
            try:
                os.remove(self.temp_db)
            except:
                pass
        self.temp_db = None

    def close(self):
        """关闭连接并清理"""
        if self.conn:
            self.conn.close()
        self.cleanup()

if __name__ == "__main__":
    try:
        connector = ZoteroConnector()
        print(f"找到数据库: {connector.database_path}")
        conn = connector.connect()
        if conn:
            print("成功连接到数据库！")
            # 测试查询
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM items")
            count = cursor.fetchone()[0]
            print(f"数据库中共有 {count} 个条目。")
            connector.close()
    except Exception as e:
        print(f"错误: {e}")
