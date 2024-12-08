import duckdb
import yaml
from jinja2 import Environment, FileSystemLoader
import os
import datetime
import pandas as pd
import argparse
import tabulate
import glob
import sys
from dotenv import load_dotenv
sys.path.append('../')
from library import Library

class Metric:
    def __init__(self,**KW):
        self.lib = Library()
        
        if KW.get('data_path'):
            self.data_path = KW['data_path']
            self.lib.log("INFO","init",f"Data Path = {self.data_path}")
        else:
            self.lib.log("ERROR","init","No data path specified")
            exit(1)
        if KW.get('parquet_path'):
            self.parquet_path = KW['parquet_path']
            self.lib.log("INFO","init",f"Parquet Path = {self.parquet_path}")
        else:
            self.lib.log("ERROR","init","No parquet path specified")
            exit(1)

        self.datestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
        self.lib.log("INFO","init",f"Datestamp = {self.datestamp}")
        self.meta = {}
        self.history = []
        self.privacy = True # Set to true to hide sensitive data during development
        self.data_tables = {}

    def resolve_ref(self, table_name):
        self.data_tables[table_name] = f"{self.data_path}/{table_name}/*.json"
        return f"read_json_auto('{self.data_tables[table_name]}')"
        
    def metric_run(self,yaml_config):
        self.lib.log("INFO","metric_run","==========================================================")
        self.data_tables = {}
        env = Environment(loader=FileSystemLoader('.'))
        env.globals['ref'] = self.resolve_ref
        template = env.from_string(yaml_config['query']).render()

        # == check if the tables defined in the SQL query actually exist
        success = True
        for table in self.data_tables:
            if len(glob.glob(self.data_tables[table])) > 0:
                self.lib.log("INFO","metric_run",f"Table {table} exists")
            else:
                self.lib.log("ERROR","metric_run",f"Table {table} does not exist ({self.data_tables[table]})")
                success = False
        if not success:
            return pd.DataFrame()

        # == execute the query
        try:
            # Execute query
            df = duckdb.query(template).df()
            self.lib.log("SUCCESS","metric_run",f"Retrieved {len(df)} records")
        except duckdb.Error as e:
            self.lib.log("ERROR","metric_run",f"Failed to execute query: {e}")
            print(template)
            return pd.DataFrame()
        
        # == check if the mandatory columns are there
        success = True
        for col in [ 'resource','resource_type','compliance','detail']:
            if not col in df.columns:
                self.lib.log("ERROR","metric_run",f" - Column {col} does not exists.  Check the SQL in your metric defintion")
                success = False
        if not success:
            return pd.DataFrame()

        # == add the meta data
        success = True       
        for f in ['metric_id','title','slo','slo_min','weight','category']:
            if f in yaml_config:
                df[f] = yaml_config[f]
                self.meta[f] = yaml_config[f]
                self.lib.log("SUCCESS","metric_run",f"meta data attribute {f} = {yaml_config[f]}")
            else:
                self.lib.log("ERROR","metric_run",f"{f} is missing in meta data")
                success = False
        if not success:
            return pd.DataFrame()
        df['datestamp'] = self.datestamp
        # == Merge the resource dimensions - TODO
        df['business_unit'] = 'undefined'
        df['team'] = 'undefined'
        df['location'] = 'undefined'

        return df

def main(**KW):
    load_dotenv()
    M = Metric(data_path = KW['data_path'],parquet_path = KW['parquet_path'])

    detail_df = pd.DataFrame()  # all the metrics will be merged into this one data frame

    for filename in os.listdir(KW['metric_path']):
        if filename.startswith('metric_') and filename.endswith('.yml'):
            metric_file = os.path.splitext(filename)[0]
            with open(f"{KW['metric_path']}/{metric_file}.yml",'rt') as y:
                metric = yaml.safe_load(y)
            
            if KW['metric'] == None or KW['metric'] == metric_file or KW['metric'] == metric['metric_id']:
                M.lib.log("INFO","main",f"Metric : {metric_file}")
                df = M.metric_run(metric)
                if df.empty:
                    M.lib.log("ERROR","main",f"There was an error generating the metric {metric_file}.  It will not be counted.",True)
                else:
                    detail_df = pd.concat([detail_df, df], ignore_index=True)

    summary = detail_df.groupby('metric_id')['compliance'].agg(['sum', 'count']).reset_index()
    summary.columns = ['metric_id', 'totalok', 'total']
    summary['score'] = round(summary['totalok'] / summary['total'] * 100,2)
    print("")
    print(tabulate.tabulate(summary,headers="keys",showindex=False))
    print("")

    try:
        detail_df.to_parquet(f"{KW['parquet_path']}/metrics.parquet")
        M.lib.log("SUCCESS","main",f"Wrote the detail dataframe to {KW['parquet_path']}/metrics.parquet")
    except:
        M.lib.log("ERROR","main",f"Unable to write the detail dataframe to {KW['parquet_path']}/metrics.parquet")
    
    M.lib.log("SUCCESS","main","All done",True)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Automated Security Reporting - Metric Generation')
    parser.add_argument('-dryrun', help='Runs the metrics for testing purposes', action='store_true')
    parser.add_argument('-metric',help='Run a dry-run test against a single metric')
    parser.add_argument('-path',help='The path where the metric yaml files are stored',default='.')
    parser.add_argument('-data',help='The path where the collector saves its files',default=os.environ.get('STORE_FILE','../data/source'))
    parser.add_argument('-parquet',help='The path where the parquet files will be saved',default='../data')
    
    args = parser.parse_args()

    main(
        metric_path     = args.path,
        data_path       = args.data,
        parquet_path    = args.parquet,
        dryrun          = args.dryrun,
        metric          = args.metric
    )
