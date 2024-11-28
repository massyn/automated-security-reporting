{%- macro weight(text) -%}
    {{ icon(text, 'red') if text >= 0.7 else icon(text, 'blue') if text <= 0.3 else icon(text, 'yellow') }}
{%- endmacro -%}

{%- macro icon(text,color) -%}
    ![icon](https://img.shields.io/badge/{{text}}-{{color}})
{%- endmacro -%}

{% set unique_categories = data | map(attribute='category') | map('default', '') | unique | list %}

# Metrics

|**Category**|**Title**|**SLO**|**Weight**|
|--|--|--|--|
{% for a in unique_categories %}|**{{ a }}**||||
{% for x in data if x['category'] == a -%}
||`{{ x['metric_id'] }}` - {{ x['title'] }}||{{ '![slo](https://img.shields.io/badge/{:.2f}%-{:.2f}%-00B050?labelColor=FFC000)'.format(x['slo_min'] * 100,x['slo'] * 100) }}|{{ weight(x['weight']) }}|
{% endfor -%}
{% endfor %}

## List of metrics

{%- for x in data %}
### {{ x['title'] }}

|**Metric id**|**Category**|**SLO**|**Weight**|
|--|--|--|--|
|`{{ x['metric_id'] }}`|{{ x['category'] }}|{{ '![slo](https://img.shields.io/badge/{:.2f}%-{:.2f}%-00B050?labelColor=FFC000)'.format(x['slo_min'] * 100,x['slo'] * 100) }}|{{ weight(x['weight']) }}|

> {{ x['description'] }}

{% endfor %}