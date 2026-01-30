- {{ title }}
  id:: {{ key }}
  type:: {{ type }}
  authors:: {{ authors | join(', ') }}
  date:: {{ date }}
  publication:: {{ publication }}
  doi:: {{ doi }}
  url:: {{ url }}
  tags:: {{ tags | join(', ') }}
  zotero_key:: {{ key }}
  {% if collections %}collections:: {{ collections | join(', ') }}{% endif %}

  ## Abstract
  {{ abstract }}

  ## Metadata
  - **Publication**: {{ publication }}
  - **Date**: {{ date }}
  - **DOI**: {% if doi %}[{{ doi }}](https://doi.org/{{ doi }}){% else %}N/A{% endif %}
  - **URL**: {% if url %}[{{ url }}]({{ url }}){% else %}N/A{% endif %}
  - **Zotero**: [Open in Zotero](zotero://select/library/items/{{ key }})
  {% if collections %}
  - **Collections**: {{ collections | join(', ') }}
  {% endif %}

  ## Authors
  {% for author in authors %}
  - [[{{ author }}]]
  {% endfor %}

  ## Attachments
  {% if attachments %}
  {% for attachment in attachment.path %}
  - [[{{ attachment }}]]
  {% endfor %}
  {% else %}
  No attachments
  {% endif %}

  ## Notes
  {% if notes %}
  {% for note in notes %}
  ### Note {{ loop.index }}
  {{ note }}
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
