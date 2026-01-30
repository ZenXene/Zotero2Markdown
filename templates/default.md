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
---

# {{ title }}

## Metadata
- **Publication**: {{ publication }}
- **Date**: {{ date }}
- **DOI**: {% if doi %}[{{ doi }}](https://doi.org/{{ doi }}){% else %}N/A{% endif %}
- **URL**: {% if url %}[{{ url }}]({{ url }}){% else %}N/A{% endif %}
- **Zotero Link**: [Zotero](zotero://select/library/items/{{ key }})
{% if collections %}
- **Collections**: {{ collections | join(', ') }}
{% endif %}

## Abstract
{{ abstract }}

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
---
{{ note }}
{% endfor %}
{% else %}
No notes
{% endif %}
