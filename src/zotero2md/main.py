import argparse
import sys
import os
import logging
from pathlib import Path
from zotero2md.database import ZoteroConnector
from zotero2md.parser import ZoteroParser
from zotero2md.exporter import MarkdownExporter
from zotero2md.config import Config
from zotero2md.logger import setup_logger, get_logger
from zotero2md.parallel_exporter import ParallelExporter
from zotero2md.item_filter import ItemFilter
from zotero2md.notion_exporter import NotionExporter
from zotero2md.obsidian_exporter import ObsidianExporter
from zotero2md.bibtex_exporter import BibTeXExporter
from zotero2md.json_exporter import JSONExporter
from zotero2md.csv_exporter import CSVExporter

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
    parser.add_argument("--parallel", action="store_true", help="启用并行导出")
    parser.add_argument("--workers", type=int, default=4, help="并行工作线程数 (默认: 4)")
    parser.add_argument("--batch-size", type=int, default=50, help="批处理大小 (默认: 50)")
    parser.add_argument("--title-regex", help="标题正则表达式过滤")
    parser.add_argument("--author-regex", help="作者正则表达式过滤")
    parser.add_argument("--abstract-regex", help="摘要正则表达式过滤")
    parser.add_argument("--start-year", type=int, help="起始年份过滤")
    parser.add_argument("--end-year", type=int, help="结束年份过滤")
    parser.add_argument("--include-tags", nargs='+', help="包含标签 (空格分隔)")
    parser.add_argument("--exclude-tags", nargs='+', help="排除标签 (空格分隔)")
    parser.add_argument("--match-all-tags", action="store_true", help="匹配所有包含标签 (默认匹配任意一个)")
    parser.add_argument("--include-collections", nargs='+', help="包含收藏夹 (空格分隔)")
    parser.add_argument("--exclude-collections", nargs='+', help="排除收藏夹 (空格分隔)")
    parser.add_argument("--filter-field", nargs=2, metavar=('FIELD', 'VALUE'), action='append', help="自定义字段过滤 (可多次使用)")
    parser.add_argument("--notion", action="store_true", help="导出到 Notion")
    parser.add_argument("--notion-api-key", help="Notion API 密钥")
    parser.add_argument("--notion-database-id", help="Notion 数据库 ID")
    parser.add_argument("--obsidian", action="store_true", help="导出到 Obsidian")
    parser.add_argument("--obsidian-vault", help="Obsidian vault 路径")
    parser.add_argument("--obsidian-folder", default="Zotero", help="Obsidian 笔记文件夹 (默认: Zotero)")
    parser.add_argument("--bibtex", action="store_true", help="导出为 BibTeX 格式")
    parser.add_argument("--bibtex-file", default="references.bib", help="BibTeX 文件名 (默认: references.bib)")
    parser.add_argument("--json", action="store_true", help="导出为 JSON 格式")
    parser.add_argument("--json-file", default="references.json", help="JSON 文件名 (默认: references.json)")
    parser.add_argument("--json-indent", type=int, default=2, help="JSON 缩进空格数 (默认: 2)")
    parser.add_argument("--csv", action="store_true", help="导出为 CSV 格式")
    parser.add_argument("--csv-file", default="references.csv", help="CSV 文件名 (默认: references.csv)")
    
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

        z_parser = ZoteroParser(connector)
        
        items = []
        for batch in z_parser.get_all_items():
            for item in batch:
                if args.include_collections or args.exclude_collections:
                    collections = z_parser.get_item_collections(item['itemID'])
                    item['collections'] = collections
                if args.include_tags or args.exclude_tags:
                    tags = z_parser.get_item_tags(item['itemID'])
                    item['tags'] = tags
                if args.filter_field:
                    metadata = z_parser.get_item_metadata(item['itemID'])
                    item['metadata'] = metadata
                items.append(item)
        
        if args.limit:
            items = items[:args.limit]
        
        item_filter = ItemFilter()
        
        if args.filter_field:
            field_filters = {}
            for field_name, field_value in args.filter_field:
                field_filters[field_name] = field_value
            items = item_filter.filter_by_custom_fields(items, field_filters)
        
        if args.title_regex or args.author_regex or args.abstract_regex:
            items = item_filter.filter_by_regex(
                items,
                title_pattern=args.title_regex,
                author_pattern=args.author_regex,
                abstract_pattern=args.abstract_regex
            )
        
        if args.start_year or args.end_year:
            items = item_filter.filter_by_date_range(
                items,
                start_year=args.start_year,
                end_year=args.end_year
            )
        
        if args.include_tags or args.exclude_tags:
            items = item_filter.filter_by_tags(
                items,
                include_tags=args.include_tags,
                exclude_tags=args.exclude_tags,
                match_all=args.match_all_tags
            )
        
        if args.include_collections or args.exclude_collections:
            items = item_filter.filter_by_collections(
                items,
                include_collections=args.include_collections,
                exclude_collections=args.exclude_collections
            )
            
        logger.info(f"找到 {len(items)} 个条目待导出...")
        
        template_dir = args.template_dir or config.get('export.template_dir', 'templates')
        template_name = args.template or config.get('export.template', 'default.md')
        convert_html = config.get('export.convert_html_notes', True)
        
        exporter = MarkdownExporter(
            template_dir=template_dir,
            template_name=template_name,
            config=config
        )
        
        if args.parallel:
            parallel_exporter = ParallelExporter(max_workers=args.workers)
            
            def export_single_item(item):
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
                    
                    return exporter.export(item_data, output_dir=args.out)
                except Exception as e:
                    logger.error(f"处理条目 {item.get('key', 'Unknown')} 失败: {e}", exc_info=True)
                    return None
            
            results = parallel_exporter.export_items_with_progress(items, export_single_item, batch_size=args.batch_size)
            
            success_count = results['success']
            skipped_count = results['skipped']
            error_count = results['error']
            
            if results['errors']:
                logger.warning(f"发生 {len(results['errors'])} 个错误")
                for error in results['errors'][:5]:
                    logger.error(f"错误详情: {error}")
        else:
            success_count = 0
            skipped_count = 0
            error_count = 0
            
            for item in items:
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
                    else:
                        skipped_count += 1
                except Exception as e:
                    logger.error(f"处理条目 {item.get('key', 'Unknown')} 失败: {e}", exc_info=True)
                    error_count += 1
        
        print(f"\n[*] 导出完成！成功: {success_count}, 跳过: {skipped_count}, 失败: {error_count}")
        print(f"[*] 文件保存在: {os.path.abspath(args.out)}")
        
        summary = exporter.get_export_summary()
        logger.info(f"导出摘要: {summary}")
        
        if args.notion:
            notion_api_key = args.notion_api_key or config.get('notion.api_key')
            notion_database_id = args.notion_database_id or config.get('notion.database_id')
            
            if not notion_api_key or not notion_database_id:
                logger.error("Notion 导出需要 API 密钥和数据库 ID")
            else:
                notion_exporter = NotionExporter(notion_api_key, notion_database_id)
                
                notion_items = []
                for item in items:
                    metadata = z_parser.get_item_metadata(item['itemID'])
                    creators = z_parser.get_item_creators(item['itemID'])
                    tags = z_parser.get_item_tags(item['itemID'])
                    notes = z_parser.get_item_notes(item['itemID'], convert_html=convert_html)
                    attachments = z_parser.get_item_attachments(item['itemID'])
                    
                    notion_items.append({
                        'title': metadata.get('title', 'Untitled'),
                        'authors': [c['name'] for c in creators],
                        'date': metadata.get('date', 'Unknown'),
                        'type': item['typeName'],
                        'doi': metadata.get('DOI', ''),
                        'url': metadata.get('url', ''),
                        'tags': tags,
                        'publication': metadata.get('publicationTitle', ''),
                        'abstract': metadata.get('abstractNote', ''),
                        'notes': notes,
                        'attachments': attachments
                    })
                
                notion_results = notion_exporter.export_items_batch(notion_items)
                print(f"\n[*] Notion 导出完成！成功: {notion_results['success']}, 失败: {notion_results['failed']}")
        
        if args.obsidian:
            obsidian_vault = args.obsidian_vault or config.get('obsidian.vault_path')
            obsidian_folder = args.obsidian_folder or config.get('obsidian.notes_folder', 'Zotero')
            
            if not obsidian_vault:
                logger.error("Obsidian 导出需要 vault 路径")
            else:
                obsidian_exporter = ObsidianExporter(obsidian_vault, obsidian_folder)
                
                obsidian_items = []
                for item in items:
                    metadata = z_parser.get_item_metadata(item['itemID'])
                    creators = z_parser.get_item_creators(item['itemID'])
                    tags = z_parser.get_item_tags(item['itemID'])
                    notes = z_parser.get_item_notes(item['itemID'], convert_html=convert_html)
                    attachments = z_parser.get_item_attachments(item['itemID'])
                    collections = z_parser.get_item_collections(item['itemID'])
                    
                    obsidian_items.append({
                        'title': metadata.get('title', 'Untitled'),
                        'authors': [c['name'] for c in creators],
                        'date': metadata.get('date', 'Unknown'),
                        'type': item['typeName'],
                        'doi': metadata.get('DOI', ''),
                        'url': metadata.get('url', ''),
                        'tags': tags,
                        'publication': metadata.get('publicationTitle', ''),
                        'abstract': metadata.get('abstractNote', ''),
                        'notes': notes,
                        'attachments': attachments,
                        'collections': collections
                    })
                
                obsidian_results = obsidian_exporter.export_items_batch(obsidian_items)
                print(f"\n[*] Obsidian 导出完成！成功: {obsidian_results['success']}, 失败: {obsidian_results['failed']}")
        
        if args.bibtex:
            bibtex_exporter = BibTeXExporter()
            
            bibtex_items = []
            for item in items:
                metadata = z_parser.get_item_metadata(item['itemID'])
                creators = z_parser.get_item_creators(item['itemID'])
                tags = z_parser.get_item_tags(item['itemID'])
                
                bibtex_items.append({
                    'key': item['key'],
                    'type': item['typeName'],
                    'title': metadata.get('title', 'Untitled'),
                    'authors': [c['name'] for c in creators],
                    'date': metadata.get('date', 'Unknown'),
                    'publication': metadata.get('publicationTitle', ''),
                    'doi': metadata.get('DOI', ''),
                    'url': metadata.get('url', ''),
                    'abstract': metadata.get('abstractNote', ''),
                    'tags': tags
                })
            
            bibtex_file = os.path.join(args.out, args.bibtex_file)
            bibtex_results = bibtex_exporter.export_items(bibtex_items, bibtex_file)
            print(f"\n[*] BibTeX 导出完成！成功: {bibtex_results['success']}, 失败: {bibtex_results['failed']}")
            print(f"[*] 文件保存在: {os.path.abspath(bibtex_file)}")
        
        if args.json:
            json_exporter = JSONExporter()
            
            json_items = []
            for item in items:
                metadata = z_parser.get_item_metadata(item['itemID'])
                creators = z_parser.get_item_creators(item['itemID'])
                tags = z_parser.get_item_tags(item['itemID'])
                notes = z_parser.get_item_notes(item['itemID'], convert_html=convert_html)
                attachments = z_parser.get_item_attachments(item['itemID'])
                collections = z_parser.get_item_collections(item['itemID'])
                
                json_items.append({
                    'key': item['key'],
                    'type': item['typeName'],
                    'title': metadata.get('title', 'Untitled'),
                    'authors': [c['name'] for c in creators],
                    'date': metadata.get('date', 'Unknown'),
                    'publication': metadata.get('publicationTitle', ''),
                    'doi': metadata.get('DOI', ''),
                    'url': metadata.get('url', ''),
                    'abstract': metadata.get('abstractNote', ''),
                    'tags': tags,
                    'notes': notes,
                    'attachments': attachments,
                    'collections': collections
                })
            
            json_file = os.path.join(args.out, args.json_file)
            json_results = json_exporter.export_items(json_items, json_file, indent=args.json_indent)
            print(f"\n[*] JSON 导出完成！成功: {json_results['success']}, 失败: {json_results['failed']}")
            print(f"[*] 文件保存在: {os.path.abspath(json_file)}")
        
        if args.csv:
            csv_exporter = CSVExporter()
            
            csv_items = []
            for item in items:
                metadata = z_parser.get_item_metadata(item['itemID'])
                creators = z_parser.get_item_creators(item['itemID'])
                tags = z_parser.get_item_tags(item['itemID'])
                attachments = z_parser.get_item_attachments(item['itemID'])
                collections = z_parser.get_item_collections(item['itemID'])
                
                csv_items.append({
                    'key': item['key'],
                    'type': item['typeName'],
                    'title': metadata.get('title', 'Untitled'),
                    'authors': [c['name'] for c in creators],
                    'date': metadata.get('date', 'Unknown'),
                    'publication': metadata.get('publicationTitle', ''),
                    'doi': metadata.get('DOI', ''),
                    'url': metadata.get('url', ''),
                    'abstract': metadata.get('abstractNote', ''),
                    'tags': tags,
                    'attachments': attachments,
                    'collections': collections
                })
            
            csv_file = os.path.join(args.out, args.csv_file)
            csv_results = csv_exporter.export_items(csv_items, csv_file)
            print(f"\n[*] CSV 导出完成！成功: {csv_results['success']}, 失败: {csv_results['failed']}")
            print(f"[*] 文件保存在: {os.path.abspath(csv_file)}")
        
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
