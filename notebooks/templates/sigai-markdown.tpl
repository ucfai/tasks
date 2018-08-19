{# Found/From: https://predictablynoisy.com/jekyll-markdown-nbconvert #}
{% extends 'markdown.tpl' %}
{#{% extends 'basic.tpl' %}#}

<!-- add div for inputs -->
{% block input %}
<div class="input_area" markdown="1">
    {{ super() }}
</div>
{% endblock %}

<!-- remove output indentations -->
{% block stream %}
{:.output_stream}
```
{{ output.text }}
```
{% endblock stream %}

{% block data_text %}
{:.output_stream}
```
{{ output.data['text/plain'] }}
```
{% endblock data_text %}

{% block traceback_line %}
{:.traceback_line}
```
{{ trackback_line | strip_ansi }}
```
{% endblock traceback_line %}

<!-- tell Jekyll to not render output as markdown -->
{% block data_html %}
<div markdown="0">
    {{ output.data['text/html'] }}
</div>
{% endblock data_html %}
