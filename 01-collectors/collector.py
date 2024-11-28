import os
import uuid
import os
import json
import datetime
import duckdb
import boto3
import botocore
import psycopg2
from psycopg2 import Error

class Collector:
    def __init__(self,meta = { 'title' : 'Collector'}):
        self.tenancy = os.environ.get('TENANCY','default')
        self.datetime = datetime.datetime.now(datetime.timezone.utc)
        self.upload_timestamp = self.datetime.strftime('%Y-%m-%d %H:%M:%S')
        self.upload_id = str(uuid.uuid4())
        self.meta = meta
       
    def test_environment(self):
        ok = True
        for v in self.meta['env']:
            # we only care if the environment variable is not set.
            if not os.environ.get(v):
                if self.meta['env'][v] is not None:
                    os.environ[v] = self.meta['env'][v]
                else:
                    self.log("WARNING",f"Environment variable {v} not found")
                    ok = False
        return ok
        
    def check_env(self,v,default = None):
        if not v in os.environ:
            if default != None:
                print(f"setting it to {default}")
                return default
        else:
            return os.environ[v]

    def log(self,sev,txt):
        print(f"{self.meta['title']} [{sev}] {txt}")

    def add_meta(self,data):
        new = []
        for i in data:
            i['_tenancy'] = self.tenancy
            i['_upload_timestamp'] = self.upload_timestamp
            i['_upload_id'] = self.upload_id
            new.append(i)
        return new
    
    def store(self,tag,data1):
        if len(data1) > 0:
            self.log("INFO",f"Storing {tag} of {len(data1)} records")

            data = self.add_meta(data1)

            self.store_file(tag,data)
            self.store_aws_s3_backup(tag,data)
            self.store_aws_s3(tag,data)
            self.store_postgres(tag,data)
            self.store_duckdb(tag,data)
        else:
            self.log("WARNING",f"No records to be written to {tag} - empty data set")

    def store_file(self,tag,data):
        target = os.environ.get('STORE_FILE','../data/source/$TAG/$TENANCY.json').replace(
            '$UUID',str(uuid.uuid4())).replace(
            '$TAG',tag).replace(
            '$TENANCY',os.environ.get('TENANCY','default')).replace(
            '$hh',self.datetime.strftime('%H')).replace(
            '$mm',self.datetime.strftime('%M')).replace(
            '$ss',self.datetime.strftime('%S')).replace(
            '$YYYY',self.datetime.strftime('%Y')).replace(
            '$MM',self.datetime.strftime('%m')).replace(
            '$DD',self.datetime.strftime('%d')
        )
        
        try:
            os.makedirs(os.path.dirname(target),exist_ok = True)        
            with open(target,"wt",encoding='UTF-8') as q:
                q.write(json.dumps(data,default=str))
            self.log("SUCCESS",f"Saving {len(data)} records for {tag} --> {target}")
        except:
            self.log("ERROR",f"Cannot write the file - {target}")

    def store_aws_s3_backup(self,tag,data):
        if self.check_env('STORE_AWS_S3_BUCKET'):
            target = os.environ.get('STORE_AWS_S3_BACKUP').replace(
                '$UUID',str(uuid.uuid4())).replace(
                '$TAG',tag).replace(
                '$TENANCY',os.environ.get('TENANCY','default')).replace(
                '$hh',self.datetime.strftime('%H')).replace(
                '$mm',self.datetime.strftime('%M')).replace(
                '$ss',self.datetime.strftime('%S')).replace(
                '$YYYY',self.datetime.strftime('%Y')).replace(
                '$MM',self.datetime.strftime('%m')).replace(
                '$DD',self.datetime.strftime('%d')
            )
            self.log("INFO",f"Saving {len(data)} records for {tag} --> s3://{self.check_env('STORE_AWS_S3_BUCKET')}/{target}")
            try:
                boto3.resource('s3').Bucket(os.environ['STORE_AWS_S3_BUCKET']).put_object(
                    ACL         = 'bucket-owner-full-control',
                    ContentType = 'application/json',
                    Key         = target,
                    Body        = json.dumps(data,default=str)
                )
                self.log("SUCCESS",f"s3.put_object - s3://{self.check_env('STORE_AWS_S3_BUCKET')}/{target}")
            except botocore.exceptions.ClientError as error:
                self.log("ERROR",f"s3.put_object - {error.response['Error']['Code']}")
            except:
                self.log("ERROR",f"s3.put_object")

    def store_aws_s3(self,tag,data):
        if self.check_env('STORE_AWS_S3_BUCKET'):
            target = os.environ.get('STORE_AWS_S3_KEY','data/tag=$TAG/year=$YYYY/month=$MM/day=$DD/$UUID.json').replace(
                '$UUID',str(uuid.uuid4())).replace(
                '$TAG',tag).replace(
                '$TENANCY',os.environ.get('TENANCY','default')).replace(
                '$hh',self.datetime.strftime('%H')).replace(
                '$mm',self.datetime.strftime('%M')).replace(
                '$ss',self.datetime.strftime('%S')).replace(
                '$YYYY',self.datetime.strftime('%Y')).replace(
                '$MM',self.datetime.strftime('%m')).replace(
                '$DD',self.datetime.strftime('%d')
            )
            self.log("INFO",f"Saving {len(data)} records for {tag} --> s3://{self.check_env('STORE_AWS_S3_BUCKET')}/{target}")
            try:
                boto3.resource('s3').Bucket(os.environ['STORE_AWS_S3_BUCKET']).put_object(
                    ACL         = 'bucket-owner-full-control',
                    ContentType = 'application/json',
                    Key         = target,
                    Body        = json.dumps(data,default=str)
                )
                self.log("SUCCESS",f"s3.put_object - s3://{self.check_env('STORE_AWS_S3_BUCKET')}/{target}")
            except botocore.exceptions.ClientError as error:
                self.log("ERROR",f"s3.put_object - {error.response['Error']['Code']}")
            except:
                self.log("ERROR",f"s3.put_object")

    def store_postgres(self,tag,data):
        host        = self.check_env('STORE_POSTGRES_HOST')
        user        = self.check_env('STORE_POSTGRES_USER')
        password    = self.check_env('STORE_POSTGRES_PASSWORD')
        dbname      = self.check_env('STORE_POSTGRES_DBNAME')
        port        = self.check_env('STORE_POSTGRES_PORT')
        schema      = self.check_env('STORE_POSTGRES_SCHEMA')

        if host:
            try:
            # Connect to your PostgreSQL database
                con = psycopg2.connect(
                    user        = user,
                    password    = password,
                    host        = host,
                    port        = port,
                    database    = dbname,
                )
            except (Exception, Error) as error:
                self.con = False
                self.log("ERROR",f"Postgres - Unable to connect : {host}")
                return

            if con:
                self.log("SUCCESS",f"Postgres : Connected : {host}")

                try:
                    cursor = con.cursor()
                    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
                    con.commit()
                except (Exception, Error) as error:
                    self.log("ERROR",f"Postgres - Unable to create schema : {error}")

                try:
                    cursor.execute(f"CREATE TABLE IF NOT EXISTS {schema}.{tag} (upload_timestamp timestamp, tenancy VARCHAR, json_data json)")
                except (Exception, Error) as error:
                    self.log("ERROR",f"Postgres - Unable to create table : {error}")
                con.commit()

                # -- insert data
                for d in data:
                    try:
                        cursor.execute(f"INSERT INTO {schema}.{tag} (upload_timestamp,tenancy,json_data) VALUES(%s,%s,%s)",(self.upload_timestamp,self.tenancy,json.dumps(d)))
                    except (Exception, Error) as error:
                        self.log("ERROR",f"Postgres - Unable to insert record : {error}")
                con.commit()
                cursor.close()
                self.log("SUCCESS",f"Postgres - {tag} - Inserted {len(data)} records.")

    def store_duckdb(self,tag,data):
        target = self.check_env('STORE_DUCKDB')
        if target:
            try:
                db = duckdb.connect(database = target, read_only = False)
                self.log("SUCCESS",f"DuckDB : Connected : {target}")
            except:
                db = False
                self.log("ERROR",f"DuckDB - Unable to connect : {target}")

            if db:
                # -- create table
                cursor = db.cursor()
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {tag} (upload_timestamp timestamp, tenancy VARCHAR, json_data TEXT)")
                db.commit()

                # -- insert data
                for d in data:
                    cursor.execute(f"INSERT INTO {tag} (upload_timestamp,tenancy,json_data) VALUES(?,?,?)",(self.upload_timestamp,self.tenancy,json.dumps(d)))
                db.commit()
                cursor.close()
                self.log("SUCCESS",f"DuckDB - {tag} - Inserted {len(data)} records.")
