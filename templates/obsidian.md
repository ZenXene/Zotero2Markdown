---
title: "{{ title }}"
authors: [{{ authors | join(', ') }}]
date: {{ date }}
type: {{ type }}
doi: {{ doi }}
url: {{ url }}
tags: [{{ tags | join(', ') }}]
zotero_key: {{ key }}
{% if collections %}collections: [{{ collections | join(', ') }}]{% endif %}
cssclass: research-paper
---

# {{ title }}

> [!abstract] Abstract
> {{ abstract }}

## Metadata
| Field | Value |
|-------|-------|
| **Publication** | {{ publication }} |
| **Date** | {{ date }} |
| **DOI** | {% if doi %}[{{ doi }}](https://doi.org/{{ doi }}){% else %}N/A{% endif %} |
| **URL** | {% if url %}[{{ url }}]({{ url }}){% else %}N/A{% endif %} |
| **Zotero** | [Open in Zotero](zotero://select/library/items/{{ key }}) |
{% if collections %}
| **Collections** | {{ collections | join(', ') }} |
{% endif %}

## Authors
{% for author in authors %}
- {{ author }}
{% endfor %}

## Attachments
{% if attachments %}
{% for attachment in attachments %}
- [{{ attachment.path }}]({{ attachment.path }})
{% endfor %}
{% else %}
No attachments
{% endif %}

## Notes
{% if notes %}
{% for note in notes %}
> [!note] Note {{ loop.index }}
> {{ note }}
{% endfor %}
{% else %}
No notes
{% endif %}

## Citations
```bibtex
@article{{ key }},
  title = {{{{ title }}}},
  author = {{{{ authors | join(' and ') }}}},
  journal = {{{{ publication }}}},
  year = {{{{ date[:4] }}}}
}
```
