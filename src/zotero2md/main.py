import argparse
import sys
import os
from pathlib import Path
from zotero2md.database import ZoteroConnector
from zotero2md.parser import ZoteroParser
from zotero2md.exporter import MarkdownExporter
from zotero2md.config import Config
from zotero2md.logger import setup_logger, get_logger

def main():
    parser = argparse.ArgumentParser(
        description="Zotero to Markdown 导出工具 (基于本地数据库)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m zotero2md.main                          # 使用默认配置导出
  python -m zotero2md.main --db /path/to/zotero.sqlite  # 指定数据库
  python -m zotero2md.main --limit 10               # 只导出前10个条目
  python -m zotero2md.main --config myconfig.yml   # 使用自定义配置
  python -m zotero2md.main --generate-config       # 生成默认配置文件
        """
    )
    parser.add_argument("--db", help="Zotero 数据库路径 (可选)")
    parser.add_argument("--out", default="output", help="输出目录 (默认: output)")
    parser.add_argument("--limit", type=int, help="限制导出的条目数量")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--template", default="default.md", help="模板文件名 (默认: default.md)")
    parser.add_argument("--template-dir", default="templates", help="模板目录 (默认: templates)")
    parser.add_argument("--log-file", help="日志文件路径")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--generate-config", action="store_true", help="生成默认配置文件")
    
    args = parser.parse_args()
    
    if args.generate_config:
        config = Config()
        config.save_default_config()
        return
    
    try:
        config = Config(args.config)
        logger = setup_logger(
            level=logging.DEBUG if args.verbose else logging.INFO,
            log_file=args.log_file or config.get('advanced.log_file')
        )
        
        logger.info("=" * 60)
        logger.info("Zotero to Markdown 导出工具启动")
        logger.info("=" * 60)
        
        db_path = args.db or config.get('database.path')
        connector = ZoteroConnector(db_path)
        logger.info(f"正在连接数据库: {connector.database_path}")
        conn = connector.connect()
        if not conn:
            logger.error("数据库连接失败")
            return

        z_parser = ZoteroParser(conn)
        items = z_parser.get_all_items()
        
        if args.limit:
            items = items[:args.limit]
            
        logger.info(f"找到 {len(items)} 个条目待导出...")

        template_dir = args.template_dir or config.get('export.template_dir', 'templates')
        template_name = args.template or config.get('export.template', 'default.md')
        convert_html = config.get('export.convert_html_notes', True)
        
        exporter = MarkdownExporter(
            template_dir=template_dir,
            template_name=template_name,
            config=config
        )
        
        success_count = 0
        skipped_count = 0
        error_count = 0
        
        for i, item in enumerate(items):
            try:
                metadata = z_parser.get_item_metadata(item['itemID'])
                creators = z_parser.get_item_creators(item['itemID'])
                tags = z_parser.get_item_tags(item['itemID'])
                notes = z_parser.get_item_notes(item['itemID'], convert_html=convert_html)
                attachments = z_parser.get_item_attachments(item['itemID'])
                collections = z_parser.get_item_collections(item['itemID'])
                
                item_data = {
                    'title': metadata.get('title', 'Untitled'),
                    'authors': [c['name'] for c in creators],
                    'date': metadata.get('date', 'Unknown'),
                    'type': item['typeName'],
                    'doi': metadata.get('DOI', ''),
                    'url': metadata.get('url', ''),
                    'tags': tags,
                    'key': item['key'],
                    'publication': metadata.get('publicationTitle', ''),
                    'abstract': metadata.get('abstractNote', ''),
                    'notes': notes,
                    'attachments': attachments,
                    'collections': collections
                }
                
                result = exporter.export(item_data, output_dir=args.out)
                
                if result:
                    success_count += 1
                    logger.debug(f"已导出: {item_data['title']}")
                else:
                    skipped_count += 1
                    logger.debug(f"已跳过: {item_data['title']}")
                
                if (i + 1) % 10 == 0 or (i + 1) == len(items):
                    print(f"\r[*] 进度: {i+1}/{len(items)}", end="", flush=True)
                    
            except Exception as e:
                error_count += 1
                logger.error(f"导出条目 {item['key']} 失败: {e}", exc_info=True)

        print(f"\n[*] 导出完成！成功: {success_count}, 跳过: {skipped_count}, 失败: {error_count}")
        print(f"[*] 文件保存在: {os.path.abspath(args.out)}")
        
        summary = exporter.get_export_summary()
        logger.info(f"导出摘要: {summary}")

        connector.close()
        logger.info("导出任务完成")
        
    except FileNotFoundError as e:
        print(f"[!] 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[!] 发生错误: {e}")
        logger.error(f"发生错误: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    import logging
    main()
