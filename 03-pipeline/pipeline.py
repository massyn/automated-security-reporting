import argparse
import os
from dotenv import load_dotenv
import sys
sys.path.append('../')
from library import Library
import pandas as pd

def update_summary(lib,parquet_file,new_df):
    # == load the parquet file
    try:
        df = pd.read_parquet(parquet_file)
    except Exception as e:
        lib.log("WARNING","write_summary",f"Error reading parquet file - {parquet_file}: {e}")
        df = pd.DataFrame()

    # == delete the old metric - this dataframe should only contain the latest
    for metric_id in new_df['metric_id'].unique():
        try:
            df = df[~((df['metric_id'] == metric_id) & (df['datestamp'] == lib.datestamp))]
        except Exception as e:
            lib.log("WARNING","write_summary",f"Unable to delete old metric - it probably doesn't exist yet: {e}")

    # == pivot the new dataframe
    new = new_df.groupby(['datestamp','metric_id','title','category','slo','slo_min','weight','business_unit','team','location']).agg({
        'compliance' : ['sum','count']
    }).reset_index()
    new.columns = ['datestamp','metric_id','title','category','slo','slo_min','weight','business_unit','team','location', 'totalok', 'total']

    # == merge the new metric
    df = pd.concat([df,new], ignore_index=True)

    # == write it back to disk
    df.to_parquet(parquet_file)
    lib.log("SUCCESS","write_summary",f"Updated summary - {parquet_file}")
    return df

def update_detail(lib,parquet_file,new_df):
        # == load the detail parquet file
        try:
            df = pd.read_parquet(parquet_file)
        except Exception as e:
            lib.log("WARNING","write_detail",f"Error reading parquet file - {parquet_file}: {e}")
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
                lib.log("WARNING","write_detail",f"Unable to delete old metric - it probably doesn't exist yet: {e}")

        # == merge the new metric
        df = pd.concat([df,new_df], ignore_index=True)

        # == write it back to disk
        df.to_parquet(parquet_file)
        lib.log("SUCCESS","write_detail",f"Updated detail - {parquet_file}")
        return df

def write_detail_csv(lib,df,csv_file):
    privacy = True # TODO
    if csv_file is not None:
        try:
            if privacy:
                df['detail'] = 'redacted'
                df['resource'] = 'redacted'
            df.to_csv(csv_file, index=False)
            lib.log("SUCCESS","write_detail_csv",f"Wrote the csv file for the dashboard - {csv_file}")
            lib.upload_to_s3(
                csv_file,
                lib.config['STORE_AWS_S3_WEB'],
                'detail.csv'
            )
        except:
            lib.log("ERROR","write_detail_csv",f"Could not write the csv file {csv_file}")

def write_summary_csv(lib,df,csv_file):
    if csv_file is not None:
        try:
            df.to_csv(csv_file, index=False)
            lib.log("SUCCESS","write_summary_csv",f"Wrote the csv file for the dashboard - {csv_file}")
            lib.upload_to_s3(
                csv_file,
                lib.config['STORE_AWS_S3_WEB'],
                'summary.csv'
            )
        except:
            lib.log("ERROR","write_summary_csv",f"Could not write the csv file {csv_file}")

def main(**KW):
    lib = Library()
    if KW.get('parquet_path'):
        lib.log("INFO","init",f"Parquet Path = {KW['parquet_path']}")
    else:
        lib.log("ERROR","init","No parquet path specified")
        exit(1)
    if KW.get('web'):
        lib.log("INFO","init",f"Web Path = {KW['web']}")
    
    # == get the df from metrics
    metrics_df = pd.read_parquet(f"{KW['parquet_path']}/metrics.parquet")

    # == find the latest files
    lib.download_from_s3(
        lib.config['STORE_AWS_S3_BUCKET'],                        # bucket
        f"{lib.config['STORE_AWS_S3_HISTORY']}/summary.parquet",  # target key
        "file",                                                 # type
        f"{KW['parquet_path']}/summary.parquet"                     # local file
    )
    lib.download_from_s3(
        lib.config['STORE_AWS_S3_BUCKET'],                        # bucket
        f"{lib.config['STORE_AWS_S3_HISTORY']}/detail.parquet",   # target key
        "file",                                                 # type
        f"{KW['parquet_path']}/detail.parquet"                      # local file
    )

    # == merge the data
    df_detail = update_detail(lib,f"{KW['parquet_path']}/detail.parquet",metrics_df)
    df_summary = update_summary(lib,f"{KW['parquet_path']}/summary.parquet",metrics_df)

    # write the csv fiile for the dashboard
    write_detail_csv(lib , df_detail , f"{KW['web']}/detail.csv")
    write_summary_csv(lib, df_summary, f"{KW['web']}/summary.csv")

    # == back it up to S3
    lib.upload_to_s3(
        f"{KW['parquet_path']}/detail.parquet",                 # filename
        lib.config['STORE_AWS_S3_BUCKET'],                      # bucket
        f"{lib.config['STORE_AWS_S3_HISTORY']}/detail.parquet"  # key
    )
    lib.upload_to_s3(
        f"{KW['parquet_path']}/summary.parquet",                 # filename
        lib.config['STORE_AWS_S3_BUCKET'],                      # bucket
        f"{lib.config['STORE_AWS_S3_HISTORY']}/summary.parquet"  # key
    )

    lib.log("SUCCESS","main","All done")

if __name__=='__main__':
    load_dotenv()
    parser = argparse.ArgumentParser(description='Automated Security Reporting - Pipeline')
    parser.add_argument('-parquet',help='The path where the parquet files will be saved',default='../data')
    parser.add_argument('-web',help='The path where the final csv files are written to',default='/var/www/html')
    
    args = parser.parse_args()

    main(
        parquet_path    = args.parquet,
        web             = args.web
    )