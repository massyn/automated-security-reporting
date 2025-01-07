import argparse
import os
from dotenv import load_dotenv
import sys
sys.path.append('../')
from library import Library
import pandas as pd
from sqlalchemy import create_engine, text

def run_sql_on_postgres(lib,file_path):
    # Load PostgreSQL credentials from environment variables
    DB_HOST = os.getenv("POSTGRES_HOST")
    DB_NAME = os.getenv("POSTGRES_DATABASE")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")  # Default to 5432 if not set
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    
    # Check that all required environment variables are set
    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
        lib.log("WARNING","run_sql_on_postgres","One or more PostgreSQL environment variables are not set.")
        return
    
    try:
        # Create the SQLAlchemy engine
        engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",isolation_level="AUTOCOMMIT")
        
        # Connect to the database
        with engine.connect() as connection:
            # Read and execute the SQL file
            with open(file_path, 'r') as sql_file:
                sql_statements = sql_file.read()
                
                # Split the SQL script into individual statements
                for statement in sql_statements.split(";"):
                    statement = statement.strip()
                    if statement:
                        connection.execute(text(statement))
            lib.log("SUCCESS","run_sql_on_postgres","SQL script executed successfully.")
    
    except Exception as e:
        lib.log("ERROR","run_sql_on_postgres",f"Error executing SQL file: {e}",True)
    
def upload_to_postgres(lib,df, table_name, if_exists="replace"):
    # Load PostgreSQL credentials from environment variables
    DB_HOST = os.getenv("POSTGRES_HOST")
    DB_NAME = os.getenv("POSTGRES_DATABASE")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")  # Default to 5432 if not set
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    
    # Check that all required environment variables are set
    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
        lib.log("WARNING","upload_to_postgres","One or more PostgreSQL environment variables are not set.")
        return
    
    # Create a SQLAlchemy engine
    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    try:
        # Write the DataFrame to the PostgreSQL database
        df.to_sql(table_name, engine, if_exists=if_exists, index=False)
        lib.log("SUCCESS","upload_to_postgres",f"Data successfully uploaded to the '{table_name}' table.")
    except Exception as e:
        lib.log("ERROR","upload_to_postgres",f"Error uploading data to PostgreSQL: {e}")
        raise

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
        except:
            lib.log("ERROR","write_detail_csv",f"Could not write the csv file {csv_file}")
        lib.upload_to_s3(
            csv_file,
            lib.config['STORE_AWS_S3_WEB'],
            'detail.csv'
        )

def write_summary_csv(lib, df, csv_file):
    if csv_file is not None:
        try:
            # Filter the DataFrame for the last 12 months
            df['datestamp'] = pd.to_datetime(df['datestamp'])
            twelve_months_ago = pd.Timestamp.now() - pd.DateOffset(months=12)
            df_filtered = df[df['datestamp'] >= twelve_months_ago]
            
            # Sort the DataFrame by datestamp
            df_filtered = df_filtered.sort_values(by='datestamp')

            # Determine the number of rows and the interval for spacing
            num_records = len(df_filtered)
            if num_records < 12:
                # If there are fewer than 12 records, just use them all
                selected_datestamps = df_filtered
            else:
                interval = num_records // 12  # Calculate interval to get 12 evenly spaced points

                # Select the 12 evenly spaced datestamps
                selected_datestamps = df_filtered.iloc[::interval][:12]  # Take every 'interval'-th row, limited to 12 records

            # Filter the DataFrame to only include the selected datestamps
            df_filtered = df_filtered[df_filtered['datestamp'].isin(selected_datestamps['datestamp'])]

            # Write the filtered DataFrame to the CSV file
            df_filtered.to_csv(csv_file, index=False)
            lib.log("SUCCESS", "write_summary_csv", f"Wrote the csv file for the dashboard - {csv_file}")
        except Exception as e:
            lib.log("ERROR", "write_summary_csv", f"Could not write the csv file {csv_file}: {e}")
            return
        
        lib.upload_to_s3(
            csv_file,
            lib.config['STORE_AWS_S3_WEB'],
            'summary.csv'
        )

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

    # == upload to postgres
    upload_to_postgres(lib,metrics_df, "detail")
    run_sql_on_postgres(lib,"postgres_summary.sql")

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

    # write the csv file for the dashboard
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