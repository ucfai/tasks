{# derived from: https://github.com/jupyter/nbconvert/blob/a6f89c3ea214ec9abe126f85b5a810216d4c9ab4/nbconvert/templates/markdown.tpl #}
{# derived from: https://gist.github.com/cscorley/9144544 #}
{# derived from: https://github.com/jupyter/nbconvert/blob/a6f89c3ea214ec9abe126f85b5a810216d4c9ab4/nbconvert/templates/html/full.tpl}
{# informed by: http://rjbaxley.com/posts/2017/02/25/Jekyll_Blogging_with_Notebooks.html #}
{% extends "basic.tpl" %}
{% from "mathjax.tpl" import mathjax %}

{# Hide the `In [X]:` prompts from Jupyter Notebooks #}
{% block in_prompt %}
{% endblock in_prompt %}

{% block empty_in_prompt %}
{% endblock empty_in_prompt %}

{# Hide the `Out [X]:` prompts from Jupyter Notebooks #}
{% block output_prompt %}
{% endblock output_prompt %}

{% block empty_output_prompt %}
{% endblock empty_output_prompt %}

{% block output_area_prompt %}
{% endblock output_area_prompt %}

{% block output %}
  {{ super() }}
{% endblock %}

{% block input %}
<div class="inner_cell">
    <div class="input_area">
        {{ cell.source | highlight_code(metadata=cell.metadata) }}
    </div>
</div>
{%- endblock input %}

{% block header %}
  <script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.1.10/require.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.0.3/jquery.min.js"></script>

  {% block ipywidgets %}
    {%- if "widgets" in nb.metadata -%}
      <script>
        (function() {
          function addWidgetsRenderer() {
              var mimeElement = document.querySelector('script[type="application/vnd.jupyter.widget-view+json"]');
              var scriptElement = document.createElement('script');
              var widgetRendererSrc = '{{ resources.ipywidgets_base_url }}@jupyter-widgets/html-manager@*/dist/embed-amd.js';
              var widgetState;
              // Fallback for older version:
              try {
                  widgetState = mimeElement && JSON.parse(mimeElement.innerHTML);
                  if (widgetState && (widgetState.version_major < 2 || !widgetState.version_major)) {
                      widgetRendererSrc = '{{ resources.ipywidgets_base_url }}jupyter-js-widgets@*/dist/embed.js';
                  }
              } catch(e) {}
              scriptElement.src = widgetRendererSrc;
              document.body.appendChild(scriptElement);
          }
          document.addEventListener('DOMContentLoaded', addWidgetsRenderer);
        }());
      </script>
    {%- endif -%}
  {% endblock ipywidgets %}

  {{ mathjax() }}

{%- endblock header %}

{% block footer %}
  {{ super() }}
{%- endblock footer %}
