# Zotero to Markdown

一个高效的 Zotero 文献导出工具，将 Zotero 中的文献元数据、笔记和附件自动转换为 Markdown 格式，支持 Obsidian、Logseq 等知识管理软件。

## 特性

- 离线工作，直接读取本地 Zotero SQLite 数据库
- 支持自定义导出模板（Jinja2）
- HTML 笔记自动转换为 Markdown
- 支持附件路径提取
- 增量更新机制
- 丰富的配置选项
- 详细的日志记录
- 预置 Obsidian 和 Logseq 模板
- **并行导出** - 支持多线程并行处理，大幅提升导出速度
- **批量处理优化** - 智能分批处理，提升大数据集性能
- **内存优化** - 流式处理，降低内存占用
- **进度显示** - 实时显示导出进度和统计信息
- **查询缓存** - 缓存元数据、标签、创建者查询，提升重复查询性能
- **正则表达式过滤** - 支持标题、作者、摘要的正则表达式过滤
- **日期范围过滤** - 按年份范围过滤文献
- **标签过滤** - 支持包含/排除标签，支持匹配所有/任意标签
- **收藏夹过滤** - 支持包含/排除收藏夹
- **自定义字段过滤** - 支持任意元数据字段的过滤
- **Notion 集成** - 直接导出到 Notion 数据库
- **Obsidian 集成** - 生成 Obsidian 格式的 Markdown 文件
- **BibTeX 导出** - 支持导出为 BibTeX 格式，用于学术引用
- **JSON 导出** - 支持导出为 JSON 格式，便于程序化处理
- **CSV 导出** - 支持导出为 CSV 格式，便于 Excel 分析
- **单元测试** - 完整的单元测试覆盖

## 安装

### 从 PyPI 安装（推荐）

```bash
pip install zotero2md
```

### 从源码安装

```bash
git clone https://github.com/yourusername/zotero2md.git
cd zotero2md
pip install -r requirements.txt
pip install -e .
```

### 开发模式安装

```bash
pip install -e ".[dev]"
```

## 快速开始

### 基本使用

```bash
python -m zotero2md.main
```

### 指定数据库路径

```bash
python -m zotero2md.main --db /path/to/zotero.sqlite
```

### 限制导出数量

```bash
python -m zotero2md.main --limit 10
```

### 使用自定义配置

```bash
python -m zotero2md.main --config myconfig.yml
```

### 使用特定模板

```bash
python -m zotero2md.main --template obsidian.md
```

### 生成默认配置文件

```bash
python -m zotero2md.main --generate-config
```

### 并行导出

```bash
python -m zotero2md.main --parallel --workers 8 --batch-size 100
```

### 正则表达式过滤

```bash
python -m zotero2md.main --title-regex "machine learning" --author-regex "Smith"
```

### 日期范围过滤

```bash
python -m zotero2md.main --start-year 2020 --end-year 2023
```

### 标签过滤

```bash
python -m zotero2md.main --include-tags "AI" "ML" --exclude-tags "review"
```

### 收藏夹过滤

```bash
python -m zotero2md.main --include-collections "Papers" "Thesis"
```

### 自定义字段过滤

```bash
python -m zotero2md.main --filter-field publicationTitle "Nature" --filter-field DOI "10."
```

### 导出到 Notion

```bash
python -m zotero2md.main --notion --notion-api-key YOUR_API_KEY --notion-database-id YOUR_DB_ID
```

### 导出到 Obsidian

```bash
python -m zotero2md.main --obsidian --obsidian-vault /path/to/vault --obsidian-folder Zotero
```

### 组合使用

```bash
python -m zotero2md.main \
  --parallel --workers 8 \
  --start-year 2020 \
  --include-tags "AI" "ML" \
  --notion --notion-api-key YOUR_API_KEY --notion-database-id YOUR_DB_ID
```

## 配置文件

配置文件支持 YAML 格式，默认查找位置：
- `zotero2md.yml` / `zotero2md.yaml`
- `config.yml` / `config.yaml`
- `~/.zotero2md.yml` / `~/.zotero2md.yaml`

### 配置示例

```yaml
database:
  path: null  # 留空自动检测
  auto_detect: true

output:
  directory: output
  filename_format: '{title}'
  sanitize_filename: true
  max_filename_length: 200

export:
  template: default.md
  template_dir: templates
  include_attachments: false
  attachment_path_type: relative
  convert_html_notes: true

filters:
  item_types: []
  tags: []
  exclude_tags: []
  collections: []

advanced:
  incremental_update: false
  overwrite_existing: true
  batch_size: 50
  log_file: null
```

## 模板

### 默认模板 (default.md)

标准 Markdown 格式，包含完整的元数据和笔记。

### Obsidian 模板 (obsidian.md)

专为 Obsidian 优化，包含：
- Callout 样式的摘要和笔记
- 表格形式的元数据
- BibTeX 引用格式
- CSS class 支持

### Logseq 模板 (logseq.md)

专为 Logseq 优化，包含：
- 属性块 (properties)
- 双向链接支持
- 嵌套列表结构

## 命令行参数

### 基本参数

| 参数 | 说明 |
|------|------|
| `--db` | Zotero 数据库路径 |
| `--out` | 输出目录（默认: output） |
| `--limit` | 限制导出的条目数量 |
| `--config` | 配置文件路径 |
| `--template` | 模板文件名 |
| `--template-dir` | 模板目录 |
| `--log-file` | 日志文件路径 |
| `--verbose` | 详细输出 |
| `--generate-config` | 生成默认配置文件 |

### 性能优化参数

| 参数 | 说明 |
|------|------|
| `--parallel` | 启用并行导出 |
| `--workers` | 并行工作线程数（默认: 4） |
| `--batch-size` | 批处理大小（默认: 50） |

### 过滤参数

| 参数 | 说明 |
|------|------|
| `--title-regex` | 标题正则表达式过滤 |
| `--author-regex` | 作者正则表达式过滤 |
| `--abstract-regex` | 摘要正则表达式过滤 |
| `--start-year` | 起始年份过滤 |
| `--end-year` | 结束年份过滤 |
| `--include-tags` | 包含标签（空格分隔） |
| `--exclude-tags` | 排除标签（空格分隔） |
| `--match-all-tags` | 匹配所有包含标签（默认匹配任意一个） |
| `--include-collections` | 包含收藏夹（空格分隔） |
| `--exclude-collections` | 排除收藏夹（空格分隔） |
| `--filter-field` | 自定义字段过滤（可多次使用） |

### 集成参数

| 参数 | 说明 |
|------|------|
| `--notion` | 导出到 Notion |
| `--notion-api-key` | Notion API 密钥 |
| `--notion-database-id` | Notion 数据库 ID |
| `--obsidian` | 导出到 Obsidian |
| `--obsidian-vault` | Obsidian vault 路径 |
| `--obsidian-folder` | Obsidian 笔记文件夹（默认: Zotero） |

## 数据库支持

自动检测以下平台的 Zotero 数据库：
- macOS: `~/Library/Application Support/Zotero/Profiles/`
- Windows: `%APPDATA%/Zotero/Zotero/Profiles/`
- Linux: `~/.zotero/zotero/`

## 项目结构

```
Zotero2Markdown-Project/
├── src/
│   └── zotero2md/
│       ├── __init__.py
│       ├── main.py              # 主入口
│       ├── database.py          # 数据库连接
│       ├── parser.py            # 数据解析（含缓存）
│       ├── exporter.py          # Markdown 导出
│       ├── config.py            # 配置管理
│       ├── logger.py            # 日志记录
│       ├── parallel_exporter.py # 并行导出
│       ├── query_cache.py       # 查询缓存
│       ├── item_filter.py       # 条目过滤
│       ├── notion_exporter.py   # Notion 导出
│       ├── obsidian_exporter.py # Obsidian 导出
│       ├── bibtex_exporter.py  # BibTeX 导出
│       ├── json_exporter.py    # JSON 导出
│       └── csv_exporter.py    # CSV 导出
├── templates/
│   ├── default.md               # 默认模板
│   ├── obsidian.md              # Obsidian 模板
│   └── logseq.md                # Logseq 模板
├── tests/
│   ├── __init__.py
│   ├── test_bibtex_exporter.py
│   ├── test_json_exporter.py
│   └── test_csv_exporter.py
├── output/                      # 导出目录
├── requirements.txt
└── README.md
```

## 测试

运行单元测试：

```bash
# 安装测试依赖
pip install -r requirements.txt

# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_bibtex_exporter.py -v
```

## 许可证

MIT License
