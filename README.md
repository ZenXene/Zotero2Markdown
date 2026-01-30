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

## 安装

```bash
pip install -r requirements.txt
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
│       ├── main.py          # 主入口
│       ├── database.py      # 数据库连接
│       ├── parser.py        # 数据解析
│       ├── exporter.py      # Markdown 导出
│       ├── config.py        # 配置管理
│       └── logger.py        # 日志记录
├── templates/
│   ├── default.md           # 默认模板
│   ├── obsidian.md          # Obsidian 模板
│   └── logseq.md            # Logseq 模板
├── output/                  # 导出目录
├── requirements.txt
└── README.md
```

## 许可证

MIT License
