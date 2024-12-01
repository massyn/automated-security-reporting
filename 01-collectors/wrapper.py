import os
import importlib

from dotenv import load_dotenv

def main(filter = ''):
    for filename in os.listdir('.'):
        if filename.startswith('src') and filename.endswith('.py'):
            plugin = os.path.splitext(filename)[0]
            print(f"Plugin : {plugin}")

            try:
                module = importlib.import_module(plugin)
                m = module.meta()
                print(m['title'])
                # Call the main function of the plugin dynamically
                module.main()
            except ModuleNotFoundError:
                print(f"Plugin '{plugin}' not found.")
            except Exception as e:
                print(f"Plugin '{plugin}' had an error {e}")

if __name__=='__main__':
    load_dotenv()
    print("Collector Wrapper")
    print("--------------------------------------")
    print(f"STORE_FILE (where the local files are stored) = {os.environ.get('STORE_FILE')}")
    print(f"STORE_AWS_S3_BUCKET (where the main data is stored) = {os.environ.get('STORE_AWS_S3_BUCKET')}")
    print(f"STORE_AWS_S3_BACKUP (where we store the last downloaded collector) = {os.environ.get('STORE_AWS_S3_BACKUP')}")
    print(f"STORE_AWS_S3_KEY (where we want to save the collector files for example if you want to keep history) = {os.environ.get('STORE_AWS_S3_KEY')}")
    main()