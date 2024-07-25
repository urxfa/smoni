import argparse
import yaml
import requests
import os

import pandas as pd
from io import StringIO

parser = argparse.ArgumentParser(prog="SMONI, Scope Monitor", description="")

parser.add_argument('-s', '--scope', help="get active current scope for a single bug bounty program")
parser.add_argument('--only-updates', action='store_true', help="show only the updated scopes on stdin")
parser.add_argument('--actives', action='store_true', help="show all current monitoring programs")
parser.add_argument('--csv', action='store_true', help="save an csv file when possible")
parser.add_argument('--config', help="config file path - default: config.yaml")
args = parser.parse_args()

silent_mode = args.only_updates

def print_message(*print_args, **kwargs):
    if not silent_mode:
        print(*print_args, **kwargs)

### Load config file for baseUrl and Actives Monitoring Programs
def loadConfigFile():
    global config

    if args.config is not None:
        config_file = os.path.join(os.getcwd(), args.config)
    else:
        home_dir = os.path.expanduser('~')
        config_file = os.path.join(home_dir, '.config/smoni/config.yaml')
        config_dir = os.path.dirname(config_file)

        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # Copy local config.yaml to $HOME/.config/smoni if it doesn't exist there
        if not os.path.isfile(config_file):
            if os.path.isfile("config.yaml"):
                with open("config.yaml", "rb") as exampleConfig:
                    with open(config_file, "wb") as finalConfig:
                        finalConfig.write(exampleConfig.read())
            else:
                raise FileNotFoundError("The configuration file does not exist and the example config.yaml is not available.")


    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
                       
def parseScope(args):
    parsedArgs = args.split(":")
    if len(parsedArgs) != 2:
        print_message("Bad arguments.\n") 
        exit(1)

    platform = parsedArgs[0]
    program = parsedArgs[1]
    
    if platform == "h1":
        h1SingleScope(program)
    else:
        print_message("\nUse: \n\th1 for HackerOne | Ex: smoni.py -s h1:dyson")
        exit("")

### Download from HackerOne - you can also save it as csv
def download_h1Scopes(program, saveFile = False, savePath = os.getcwd()):
    baseUrl = config["hackerone"]["baseUrl"]

    url = baseUrl.replace("$PROGRAM$", program)
    r = requests.get(url)
    
    if r.status_code != 200:
        print_message("Error while downloading scope from HackerOne...")
        exit()

    if saveFile:
        if "Content-Disposition" in r.headers:
            content_disposition = r.headers["Content-Disposition"]
            filename = content_disposition.split('filename=')[1].strip('"')
        else:
            filename = f"{program}.csv"

        filePath = os.path.join(savePath, filename)
        with open(filePath, "wb") as file:
            file.write(r.content)
    
    data = r.content.decode("utf-8")
    return data

### Handle .csv files
def h1SingleScope(program):
    csvFile = download_h1Scopes(program, args.csv)
    csvData = StringIO(csvFile)
    
    df = pd.read_csv(csvData)
    df_actives = df[(df["asset_type"] == "URL") & (df["eligible_for_bounty"] == True) & (df["eligible_for_submission"] == True)]
    
    
    df_identifier = df_actives["identifier"]
    for i in df_identifier:
        print_message(i)

## Return all current monitoring bug bounty programs
def showActives():
    h1_actives = config["hackerone"]["watch"]
    
    print_message("HackerOne: ")
    for i in h1_actives:
        print_message(f" * {i}")
    print_message()

def checkUpdates(program, path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    if len(files) == 0:
        print_message(f" - - Recently added program: {program}\n")
        download_h1Scopes(program, True, path)
        return []
    else:
        oldUpdateFile = max(files, key=lambda f: os.path.getmtime(os.path.join(path, f)))
        newUpdateFile = download_h1Scopes(program, True, path)

        old_df = pd.read_csv(os.path.join(path, oldUpdateFile))
        
        new_csvData = StringIO(newUpdateFile)
        new_df = pd.read_csv(new_csvData)

        if old_df.equals(new_df):
            print_message(f"No updates on {program.capitalize()}!\n")
            os.remove(os.path.join(path, oldUpdateFile))
            return []
        else:
            print_message(f"Updates on {program.capitalize()}!\n")
            df_diff = pd.concat([new_df, old_df]).drop_duplicates(keep=False)
            df_actives = df_diff[(df_diff["eligible_for_bounty"] == True) & 
                                (df_diff["eligible_for_submission"] == True)]

            df_identifier = df_actives["identifier"]
            
            for i in df_identifier:
                print(i)

            os.remove(os.path.join(path, oldUpdateFile))

            return df_identifier.to_list()
            
def h1ScopesWatcher():
    h1_actives = config["hackerone"]["watch"]
    home_dir = os.path.expanduser('~')

    path = os.path.join(home_dir, '.config/smoni/db')
  
    if not os.path.exists(path):
        os.makedirs(path)
    
    for program in h1_actives:
        print_message(f"Checking Updates for {program.capitalize()}")
        program_folderPath = os.path.join(path, program)

        if not os.path.exists(program_folderPath):
            os.makedirs(program_folderPath)

        checkUpdates(program, program_folderPath)

def main(): 
    print_message(r"""
███████ ███    ███  ██████  ███    ██ ██ 
██      ████  ████ ██    ██ ████   ██ ██ 
███████ ██ ████ ██ ██    ██ ██ ██  ██ ██ 
     ██ ██  ██  ██ ██    ██ ██  ██ ██ ██ 
███████ ██      ██  ██████  ██   ████ ██ 
    """)

    if args.scope is not None:
        parseScope(args.scope)
    elif args.actives:
        showActives()
    else:
        h1ScopesWatcher()

if __name__ == '__main__':
    loadConfigFile()
    main()


    
