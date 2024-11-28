import sys
import os
from jinja2 import Environment, FileSystemLoader
import importlib
import re
import yaml

def extract_store(contents):
    pattern = r'store\(["\']([^"\']+)["\']'
    filenames = re.findall(pattern, contents)
    return filenames

def collector_data(src):
    data = []
    if src not in sys.path:
        sys.path.append(src)
    for filename in sorted(os.listdir(src)):
        if filename.startswith('src') and filename.endswith('.py'):
            plugin = os.path.splitext(filename)[0]
            print(f"Plugin : {plugin}")
            try:
                module = importlib.import_module(f"{src}.{plugin}")
                z = module.meta()
                with open(f"{src}/{filename}",'rt',encoding='utf-8') as q:
                    contents = q.read()
                    z['store'] = extract_store(contents)
                z['filename'] = filename
                data.append(z)
            except ModuleNotFoundError:
                print(f"Plugin '{plugin}' not found.")
            except Exception as e:
                print(f"Plugin '{plugin}' had an error {e}")
    return data

def metrics_data(src):
    data = []
    if src not in sys.path:
        sys.path.append(src)
    for filename in sorted(os.listdir(src)):
        if filename.startswith('metric_') and filename.endswith('.yml'):
            metric = os.path.splitext(filename)[0]
            print(f"Metric : {metric}")
            with open(f"{src}/{metric}.yml","rt",encoding='utf-8') as y:
                data.append(yaml.safe_load(y))
    return data

def render_jinja(data,template,output):
    template_dir = '99-templates'
    env = Environment(loader=FileSystemLoader(template_dir)).get_template(template)
    result = env.render(data = data)
    print(f"Writing {output}")
    with open(output,'wt',encoding='utf-8') as q:
        q.write(result)

col = collector_data('01-collectors')
met = metrics_data('02-metrics')

render_jinja(col,'collectors.md','00-docs/collectors.md')
render_jinja(met,'metrics.md','00-docs/metrics.md')