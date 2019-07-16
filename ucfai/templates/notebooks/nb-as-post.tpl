{# derived from: https://gist.github.com/cscorley/9144544 #}
{# informed by: http://rjbaxley.com/posts/2017/02/25/Jekyll_Blogging_with_Notebooks.html #}
{% extends 'markdown.tpl' %}

{%- block header -%}
---
layout: post
title: "{{ resources['ucfai']['title'] }}"
date: "{{ resources['ucfai']['date'] }}"
authors:
    {% for author in resources['ucfai']['authors'] %}
    - {{ author['github'] }}
    {% endfor %}
categories:
    {% for category in resources['ucfai']['categories'] %}
    - {{ category }}
    {% endfor %}
tags:
    {% for tag in resources['ucfai']['tags'] %}
    - {{ tag }}
    {% endfor %}
description: >-
    {{ resources['ucfai']['description'] }}
---
{%- endblock header -%}


{% block input %}
{{ '{% highlight python %}' }}
{{ cell.source }}
{{ '{% endhighlight %}' }}
{% endblock input %}

{% block data_svg %}
![svg]({{ output.metadta.filenames['image/svg+xml'] | path2support }})
{% endblock data_svg %}

{% block data_png %}
![png]({{ output.metadta.filenames['image/png'] | path2support }})
{% endblock data_png %}

{% block data_jpg %}
![jpeg]({{ output.metadta.filenames['image/jpeg'] | path2support }})
{% endblock data_jpg %}

{% block markdowncell scoped %}
{{ cell.source | wrap_text(80) }}
{% endblock markdowncell %}

{% block headingcell scoped %}
{{ '#' * cell.level }} {{ cell.source | replace('\n', ' ') }}
{% endblock headingcell %}

