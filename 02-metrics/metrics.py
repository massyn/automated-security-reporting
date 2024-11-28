import duckdb
import yaml
from jinja2 import Environment, FileSystemLoader
import os
import datetime
import pandas as pd
import argparse
import tabulate

class Metric:
    def __init__(self,**KW):
        if KW.get('data_path'):
            self.data_path = KW['data_path']
            self.log('INFO',f"Data Path = {self.data_path}")
        else:
            self.log('ERROR',"No data path specified")
            exit(1)
        if KW.get('parquet_path'):
            self.parquet_path = KW['parquet_path']
            self.log('INFO',f"Parquet Path = {self.parquet_path}")
        else:
            self.log('ERROR',"No parquet path specified")
            exit(1)
        self.datestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
        self.log("INFO",f"Datestamp = {self.datestamp}")
        self.meta = {}
        self.history = []

    def write_summary(self,new_df):
        # == load the parquet file
        try:
            df = pd.read_parquet(f'{self.parquet_path}/summary.parquet')
        except Exception as e:
            self.log('WARNING',f"Error reading parquet file: {e}")
            df = pd.DataFrame()

        # == delete the old metric - this dataframe should only contain the latest
        for metric_id in new_df['metric_id'].unique():
            try:
                df = df[~((df['metric_id'] == metric_id) & (df['datestamp'] == self.datestamp))]
            except Exception as e:
                self.log('WARNING',f"Unable to delete old metric - it probably doesn't exist yet: {e}")

        # == pivot the new dataframe
        new = new_df.groupby(['datestamp','metric_id','title','category','slo','slo_min','weight','business_unit','team','location']).agg({
            'compliance' : ['sum','count']
        }).reset_index()
        new.columns = ['datestamp','metric_id','title','category','slo','slo_min','weight','business_unit','team','location', 'total_ok', 'total']

        # == merge the new metric
        df = pd.concat([df,new], ignore_index=True)

        # == write it back to disk
        df.to_parquet(f'{self.parquet_path}/summary.parquet')
        self.log('SUCCESS','Updated summary')

    def write_detail(self,new_df):
        # == load the detail parquet file
        try:
            df = pd.read_parquet(f'{self.parquet_path}/detail.parquet')
        except Exception as e:
            self.log('WARNING',f"Error reading parquet file: {e}")
            df = pd.DataFrame({
                'datestamp': pd.to_datetime([]),
                'metric_id': pd.Series(dtype='str'),
                'title': pd.Series(dtype='str'),
                'resource': pd.Series(dtype='str'),
                'resource_type': pd.Series(dtype='str'),
                'detail': pd.Series(dtype='str'),
                'slo': pd.Series(dtype='float'),
                'slo_min': pd.Series(dtype='float'),
                'weight': pd.Series(dtype='float'),
                'compliance': pd.Series(dtype='float'),
                'business_unit' : pd.Series(dtype='str'),
                'team' : pd.Series(dtype='str'),
                'location' : pd.Series(dtype='str'),
            })
        
        # == delete the old metric - this dataframe should only contain the latest
        for metric_id in new_df['metric_id'].unique():
            try:
                df = df[df['metric_id'] != metric_id]
            except Exception as e:
                self.log('WARNING',f"Unable to delete old metric - it probably doesn't exist yet: {e}")

        # == merge the new metric
        df = pd.concat([df,new_df], ignore_index=True)

        # == write it back to disk
        df.to_parquet(f'{self.parquet_path}/detail.parquet')
        self.log('SUCCESS','Updated detail')

    def log(self,sev,txt):
        print(f"[{sev}] - {txt}")

    def resolve_ref(self, table_name):
        return f"read_json_auto('{self.data_path}/{table_name}/*.json')"
        
    def metric_init(self,data):
        for f in ['metric_id','title','slo','slo_min','weight','category']:
            if f in data:
                self.meta[f] = data[f]
                self.log("SUCCESS",f"meta data attribute {f} = {data[f]}")
            else:
                self.log('ERROR',f"{f} is missing in meta data")

    def metric_run(self,data):
        env = Environment(loader=FileSystemLoader('.'))
        env.globals['ref'] = self.resolve_ref
        template = env.from_string(data['query']).render()
        
        try:
            # Execute query
            df = duckdb.query(template).df()
            self.log("SUCCESS",f"Retrieved {len(df)} records")
        except duckdb.Error as e:
            self.log('ERROR',f"Failed to execute query: {e}")
            print(template)
            return

        # == check if the mandatory columns are there
        error = False
        for col in [ 'resource','resource_type','compliance','detail']:
            if not col in df.columns:
                self.log('ERROR',f' - Column {col} does not exists.  Check the SQL in your metric defintion')
                error = True
        if error:
            return False
        else:
            return df

    def add(self,df):
        if self.meta == {}:
            self.log("ERROR","You did not initialise the metric.")
            return
        
        df['datestamp'] = self.datestamp
            
        # == merge the metric library into the df
        for m in self.meta:
            df[m] = self.meta[m]

        # == Merge the resource dimensions - TODO
        df['business_unit'] = 'undefined'
        df['team'] = 'undefined'
        df['location'] = 'undefined'

        return df
    
    def summary(self,df):
        metric_id = df['metric_id'].unique()[0]
        t = df['compliance'].agg(['sum','count'])
        self.log('INFO',f"Metric {metric_id} Score : {t['sum']} / {t['count']} = {t['sum'] / t['count']:.2%}")
        self.history.append({ 
            "metric_id" : metric_id,
            "totalok"   : t['sum'],
            "total"     : t['count'],
            "score"     : f"{t['sum'] / t['count'] * 100:.2f}%"
        })

def main(**KW):
    M = Metric(data_path = KW['data_path'],parquet_path = KW['parquet_path'])

    for filename in os.listdir(KW['metric_path']):
        if filename.startswith('metric_') and filename.endswith('.yml'):
            metric_file = os.path.splitext(filename)[0]
            with open(f"{KW['metric_path']}/{metric_file}.yml",'rt') as y:
                metric = yaml.safe_load(y)
            
            if KW['metric'] == None or KW['metric'] == metric_file or KW['metric'] == metric['metric_id']:
                M.log("INFO",f"Metric : {metric_file}")
                M.metric_init(metric)
                df = M.metric_run(metric)
                if df is not None:
                    if KW['metric'] == None and not KW['dryrun']:
                        df = M.add(df)
                        M.summary(df)
                        M.write_detail(df)
                        M.write_summary(df)
                    else:
                        M.log('WARNING','We are in dryrun mode -- writing nothing to disk')
                        print(df)
                else:
                    M.log('ERROR','There was an error generating the metric.  It will not be counted.')
    
    M.log("SUCCESS","All done")
    print("")
    print(tabulate.tabulate(M.history,headers="keys"))

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Automated Security Reporting - Metric Generation')
    parser.add_argument('-dryrun', help='Runs the metrics for testing purposes', action='store_true')
    parser.add_argument('-metric',help='Run a dry-run test against a single metric')
    parser.add_argument('-path',help='The path where the metric yaml files are stored',default='.')
    parser.add_argument('-data',help='The path where the collector saves its files',default='../data/source')
    parser.add_argument('-parquet',help='The path where the parquet files will be saved',default='../data')
    #parser.add_argument('-s3',help='The AWS S3 bucket path where the parquet files will be backed up and retrieved from')

    args = parser.parse_args()

    main(
        metric_path     = args.path,
        data_path       = args.data,
        parquet_path    = args.parquet,
        dryrun          = args.dryrun,
        metric          = args.metric
    )
