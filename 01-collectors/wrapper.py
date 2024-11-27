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
    main()