{# derived from: https://gist.github.com/cscorley/9144544 #}
{# informed by: http://rjbaxley.com/posts/2017/02/25/Jekyll_Blogging_with_Notebooks.html #}
{% extends 'markdown.tpl' %}

{%- block header -%}
---
layout: post
title: {{ resources['metadata']['title'] }}
date: {{ resources['metadata']['date'] }}
authors: 
    {% for author in resources["metadata"]["authors"] -%}
    - {{ author["github"] }}
    {%- endfor %}
categories: {{ resources["metadata"]["categories"] or [] }}
tags: {{ resources["metadata"]["tags"] or [] }}
description: >-
    {{ resources['metadata']['description'] }}
---
{%- endblock header -%}


{% block input %}
{{ '{% highlight python %}' }}
{{ cell.source }}
{{ '{% endhighlight %}' }}
{% endblock input %}

{% block data_svg %}
![svg]({{ output.metadta.filenames['image/svg+xml'] }})
{% endblock data_svg %}

{% block data_png %}
![png]({{ output.metadta.filenames['image/png'] }})
{% endblock data_png %}

{% block data_jpg %}
![jpeg]({{ output.metadta.filenames['image/jpeg'] }})
{% endblock data_jpg %}

{% block markdowncell scoped %}
{% if cell["metadata"].get("type", "") != "sigai_heading" -%}
{# {% if not cell["metadata"].get("nb_major_heading", False) -%} #}
{{ cell.source | wrap_text(80) }}
{%- endif %}
{% endblock markdowncell %}

{% block headingcell scoped %}
{{ '#' * cell.level }} {{ cell.source | replace('\n', ' ') }}
{% endblock headingcell %}

