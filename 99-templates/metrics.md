{% set unique_categories = data | map(attribute='category') | map('default', '') | unique | list %}

# Metrics

|**Category**|**Metric id**|**Title**|**SLO**|**Weight**|
|--|--|--|--|--|
{% for a in unique_categories %}|**{{ a }}**|||||
{% for x in data if x['category'] == a -%}
||`{{ x['metric_id'] }}`|{{ x['title'] }}|{{ "{:.2f}".format(x['slo_min'] * 100) }}% - {{ "{:.2f}".format(x['slo'] * 100) }}%|{{ x['weight'] }}|
{% endfor -%}
{% endfor %}

## List of metrics

{%- for x in data %}
### {{ x['title'] }}

|**Metric id**|**Category**|**SLO**|**Weight**|
|--|--|--|--|
|`{{ x['metric_id'] }}`|{{ x['category'] }}|{{ "{:.2f}".format(x['slo_min'] * 100) }}% - {{ "{:.2f}".format(x['slo'] * 100) }}%|{{ x['weight'] }}|

> {{ x['description'] }}

{% endfor %}