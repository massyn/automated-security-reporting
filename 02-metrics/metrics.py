import duckdb
import yaml
from jinja2 import Environment, FileSystemLoader
import os
import datetime
import pandas as pd
import argparse
import tabulate
import boto3
from botocore.exceptions import ClientError
import glob

class Metric:
    def __init__(self,**KW):
        self.error_count = { "SUCCESS" : 0, "INFO" : 0, "WARNING" : 0, "ERROR" : 0}
        self.config = {
            "STORE_AWS_S3_BUCKET"   : os.environ.get('STORE_AWS_S3_BUCKET',''),
            "STORE_AWS_S3_HISTORY"  : os.environ.get('STORE_AWS_S3_HISTORY','history'),
            "STORE_AWS_S3_WEB"      : os.environ.get('STORE_AWS_S3_WEB',''),
        }
        if KW.get('data_path'):
            self.data_path = KW['data_path']
            self.log("INFO","init",f"Data Path = {self.data_path}")
        else:
            self.log("ERROR","init","No data path specified")
            exit(1)
        if KW.get('parquet_path'):
            self.parquet_path = KW['parquet_path']
            self.log("INFO","init",f"Parquet Path = {self.parquet_path}")
        else:
            self.log("ERROR","init","No parquet path specified")
            exit(1)
        if KW.get('web'):
            self.web = KW['web']
            self.log("INFO","init",f"Web Path = {self.web}")
        self.datestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
        self.log("INFO","init",f"Datestamp = {self.datestamp}")
        self.meta = {}
        self.history = []
        self.privacy = True # Set to true to hide sensitive data during development
        self.data_tables = {}

    def upload_to_s3(self,file_name,bucket,key):
        self.log("INFO","upload_to_s3",f"Bucket = {bucket} , key = {key}, file_name = {file_name} ...")
        if not os.path.exists(file_name):
            self.log("WARNING","upload_to_s3",f"Not uploading to S3 because {file_name} does not exist")
        else:
            if bucket != None and bucket != '' and key != None and os.path.exists(file_name):
                self.log("INFO","upload_to_s3",f"Uploading {file_name} to s3://{bucket}/{key}")
                s3_client = boto3.client('s3')
                try:
                    s3_client.upload_file(file_name, bucket, key, ExtraArgs={'ACL': 'bucket-owner-full-control'})
                    self.log("SUCCESS","upload_to_s3",f"Upload complete.")
                except ClientError as e:
                    self.log("ERROR","upload_to_s3",e)
                    return False
                return True
            else:
                self.log("WARNING","upload_to_s3","Not uploading to S3 because none of the variables are defined.")

    def download_from_s3(self,file_name,key):
        if self.config['STORE_AWS_S3_HISTORY'] != '':
            if os.path.exists(file_name):
                self.log("INFO","download_from_s3",f"File {file_name} already exists, so we will skip the overwrite")
            else:
                self.log("INFO,","download_from_s3",f"Starting the download")
                s3_client = boto3.client('s3')
                try:
                    s3_client.download_file(self.config['STORE_AWS_S3_BUCKET'], f"{self.config['STORE_AWS_S3_HISTORY']}/{key}", file_name)
                    self.log("SUCCESS","download_from_s3",f"Downloaded from S3 to {key}")
                except ClientError as e:
                    self.log("ERROR","download_from_s3",e)
                    return False
                return True
        return None

    def write_summary(self,new_df,csv_file):
        # == load the parquet file
        try:
            df = pd.read_parquet(f"{self.parquet_path}/summary.parquet")
        except Exception as e:
            self.log("WARNING","write_summary",f"Error reading parquet file: {e}")
            df = pd.DataFrame()

        # == delete the old metric - this dataframe should only contain the latest
        for metric_id in new_df['metric_id'].unique():
            try:
                df = df[~((df['metric_id'] == metric_id) & (df['datestamp'] == self.datestamp))]
            except Exception as e:
                self.log("WARNING","write_summary",f"Unable to delete old metric - it probably doesn't exist yet: {e}")

        # == pivot the new dataframe
        new = new_df.groupby(['datestamp','metric_id','title','category','slo','slo_min','weight','business_unit','team','location']).agg({
            'compliance' : ['sum','count']
        }).reset_index()
        new.columns = ['datestamp','metric_id','title','category','slo','slo_min','weight','business_unit','team','location', 'totalok', 'total']

        # == merge the new metric
        df = pd.concat([df,new], ignore_index=True)

        # == write it back to disk
        df.to_parquet(f"{self.parquet_path}/summary.parquet")
        self.log("SUCCESS","write_summary","Updated summary")
        
        if csv_file is not None:
            try:
                df.to_csv(csv_file, index=False)
                self.log("SUCCESS","write_summary",f"Wrote the csv file for the dashboard - {csv_file}")
                self.upload_to_s3(
                    csv_file,
                    self.config['STORE_AWS_S3_WEB'],
                    'summary.csv'
                )
            except:
                self.log("ERROR","write_summary",f"Could not write the csv file {csv_file}")

    def write_detail(self,new_df,csv_file = None):
        # == load the detail parquet file
        try:
            df = pd.read_parquet(f"{self.parquet_path}/detail.parquet")
        except Exception as e:
            self.log("WARNING","write_detail",f"Error reading parquet file: {e}")
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
                self.log("WARNING","write_detail",f"Unable to delete old metric - it probably doesn't exist yet: {e}")

        # == merge the new metric
        df = pd.concat([df,new_df], ignore_index=True)

        # == write it back to disk
        df.to_parquet(f"{self.parquet_path}/detail.parquet")
        self.log("SUCCESS","write_detail","Updated detail")
        if csv_file is not None:
            try:
                if self.privacy:
                    df['detail'] = 'redacted'
                    df['resource'] = 'redacted'
                df.to_csv(csv_file, index=False)
                self.log("SUCCESS","write_detail",f"Wrote the csv file for the dashboard - {csv_file}")
                self.upload_to_s3(
                    csv_file,
                    self.config['STORE_AWS_S3_WEB'],
                    'detail.csv'
                )
            except:
                self.log("ERROR","write_detail",f"Could not write the csv file {csv_file}")

    def log(self,sev,mod,txt = None):
        ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%H:%S')
        print(f"{ts} [{sev:<8}] {mod:<16} : {txt}")
        if not sev in self.error_count:
            self.error_count[sev] = 0
        self.error_count[sev] += 1

    def resolve_ref(self, table_name):
        self.data_tables[table_name] = f"{self.data_path}/{table_name}/*.json"
        return f"read_json_auto('{self.data_tables[table_name]}')"
        
    def metric_init(self,data):
        self.log("INFO","metric_init","==========================================================")
        self.data_tables = {}
        for f in ['metric_id','title','slo','slo_min','weight','category']:
            if f in data:
                self.meta[f] = data[f]
                self.log("SUCCESS","metric_init",f"meta data attribute {f} = {data[f]}")
            else:
                self.log("ERROR","metric_init",f"{f} is missing in meta data")

    '''
        check if the tables referenced in the SQL queries actually exist.  If not, go grab them
        from the backup storage
    '''
    def validate_tables(self):
        success = True
        for table in self.data_tables:
            if len(glob.glob(self.data_tables[table])) > 0:
                self.log("INFO","validate_table",f"Table {table} exists")
            else:
                self.log("WARNING","validate_table",f"Table {table} does not exist ({self.data_tables[table]})")
                success = False
        return success

    def metric_run(self,data):
        env = Environment(loader=FileSystemLoader('.'))
        env.globals['ref'] = self.resolve_ref
        template = env.from_string(data['query']).render()

        if not self.validate_tables():
            return False

        try:
            # Execute query
            df = duckdb.query(template).df()
            self.log("SUCCESS","metric_run",f"Retrieved {len(df)} records")
        except duckdb.Error as e:
            self.log("ERROR","metric_run",f"Failed to execute query: {e}")
            print(template)
            return

        # == check if the mandatory columns are there
        error = False
        for col in [ 'resource','resource_type','compliance','detail']:
            if not col in df.columns:
                self.log("ERROR","metric_run",f" - Column {col} does not exists.  Check the SQL in your metric defintion")
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
        self.log("INFO","summary",f"Metric {metric_id} Score : {t['sum']} / {t['count']} = {t['sum'] / t['count']:.2%}")
        self.history.append({ 
            "metric_id" : metric_id,
            "totalok"   : t['sum'],
            "total"     : t['count'],
            "score"     : f"{t['sum'] / t['count'] * 100:.2f}%"
        })

def main(**KW):
    M = Metric(data_path = KW['data_path'],parquet_path = KW['parquet_path'],web = '/var/www/html')

    if KW['metric'] == None and not KW['dryrun']:
        M.download_from_s3(f"{M.parquet_path}/summary.parquet","summary.parquet")
        M.download_from_s3(f"{M.parquet_path}/detail.parquet","detail.parquet")

    for filename in os.listdir(KW['metric_path']):
        if filename.startswith('metric_') and filename.endswith('.yml'):
            metric_file = os.path.splitext(filename)[0]
            with open(f"{KW['metric_path']}/{metric_file}.yml",'rt') as y:
                metric = yaml.safe_load(y)
            
            if KW['metric'] == None or KW['metric'] == metric_file or KW['metric'] == metric['metric_id']:
                M.log("INFO","main",f"Metric : {metric_file}")
                M.metric_init(metric)
                df = M.metric_run(metric)
                if df is not None:
                    if KW['metric'] == None and not KW['dryrun']:
                        df = M.add(df)
                        M.summary(df)
                        M.write_detail(df,f"{M.web}/detail.csv")
                        M.write_summary(df,f"{M.web}/summary.csv")
                    else:
                        M.log("WARNING","main","We are in dryrun mode -- writing nothing to disk")
                        print(df)
                else:
                    M.log("ERROR","main","There was an error generating the metric.  It will not be counted.")
    
    if KW['metric'] == None and not KW['dryrun']:
        M.upload_to_s3(
            f"{M.parquet_path}/summary.parquet",
            M.config['STORE_AWS_S3_BUCKET'],
            f"{M.config['STORE_AWS_S3_HISTORY']}/summary.parquet"
        )
        M.upload_to_s3(
            f"{M.parquet_path}/detail.parquet",
            M.config['STORE_AWS_S3_BUCKET'],
            f"{M.config['STORE_AWS_S3_HISTORY']}/detail.parquet"
        )

    if M.error_count['ERROR'] == 0:
        M.log("SUCCESS","main","All done")
    else:
        M.log("ERROR","main",f"All done - with {M.error_count['ERROR']} errors")
    print("")
    print(tabulate.tabulate(M.history,headers="keys"))

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Automated Security Reporting - Metric Generation')
    parser.add_argument('-dryrun', help='Runs the metrics for testing purposes', action='store_true')
    parser.add_argument('-metric',help='Run a dry-run test against a single metric')
    parser.add_argument('-path',help='The path where the metric yaml files are stored',default='.')
    parser.add_argument('-data',help='The path where the collector saves its files',default=os.environ.get('STORE_FILE','../data/source'))
    parser.add_argument('-parquet',help='The path where the parquet files will be saved',default='../data')
    parser.add_argument('-web',help='The path where the final csv files are written to',default='/var/www/html/public')
    
    args = parser.parse_args()

    main(
        metric_path     = args.path,
        data_path       = args.data,
        parquet_path    = args.parquet,
        dryrun          = args.dryrun,
        metric          = args.metric,
        web             = args.web
    )
