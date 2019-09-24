{%- block header -%}
---
layout: meeting
title: {{ resources["metadata"]["title"] }}
date: {{ resources["metadata"]["date"] }}
authors:
    {% for author in resources["metadata"]["authors"] -%}
    - {{ author["github"] }}
    {% endfor %}
categories: {{ resources["metadata"]["categories"] or [] }}
tags: {{ resources["metadata"]["tags"] or [] }}
description: >-
    {{ resources["metadata"]["description"] }}
---
{%- endblock header -%}
