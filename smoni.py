import argparse
import yaml
import requests
import os

import pandas as pd
from io import StringIO

parser = argparse.ArgumentParser(prog="SMONI, Scope Monitor", description="")

parser.add_argument('-s', '--scope', help="get active current scope for a single bug bounty program")
parser.add_argument('-o', '--output',  help="output filename")
parser.add_argument('--silent', action='store_false', help="it will not show results on STDIN")
parser.add_argument('--csv', action='store_true', help="save an csv file when possible")
parser.add_argument('--config', help="config file path - default: config.yaml", default="config.yaml")
args = parser.parse_args()
                                                         
def parseScope(args):
    parsedArgs = args.split(":")
    
    if len(parsedArgs) != 2:
        print("Bad arguments.\n") 
        exit(1)

    platform = parsedArgs[0]
    program = parsedArgs[1]
    
    if platform == "h1":
        h1SingleScope(program)
    else:
        print("\nUse: \n\th1 for HackerOne | Ex: smoni.py -s h1:dyson")
        exit("")

### Load config file for baseUrl and Actives Monitoring Programs
def loadConfigFile(config):
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config

### Download from HackerOne - you can also save it as csv
def download_h1Scopes(program, saveFile = False):
    config = loadConfigFile(args.config)
    
    baseUrl = config["hackerone"]["baseUrl"]

    url = baseUrl.replace("$PROGRAM$", program)
    r = requests.get(url)
    
    if r.status_code != 200:
        print("Error while downloading scope from HackerOne...")
        exit()

    if saveFile:
        currentDir = os.getcwd()

        if "Content-Disposition" in r.headers:
            content_disposition = r.headers["Content-Disposition"]
            filename = content_disposition.split('filename=')[1].strip('"')
        else:
            filename = f"{program}.csv"

        filePath = os.path.join(currentDir, filename)
        with open(filePath, "wb") as file:
            file.write(r.content)
            print(f"Saved on {filename}\n")
    
    data = r.content.decode("utf-8")
    return data

### Handle .csv files
def h1SingleScope(program):
    csvFile = download_h1Scopes(program, args.csv)
    csvData = StringIO(csvFile)
    
    df = pd.read_csv(csvData)
    df_actives = df[(df["asset_type"] == "URL") & (df["eligible_for_bounty"] == True) & (df["eligible_for_submission"] == True)]
    
    if args.silent:
        df_identifier = df_actives["identifier"]
        for i in df_identifier:
            print(i)
    
def main():    
    print(r"""
███████ ███    ███  ██████  ███    ██ ██ 
██      ████  ████ ██    ██ ████   ██ ██ 
███████ ██ ████ ██ ██    ██ ██ ██  ██ ██ 
     ██ ██  ██  ██ ██    ██ ██  ██ ██ ██ 
███████ ██      ██  ██████  ██   ████ ██ 
    """)

    if args.scope is not None:
        parseScope(args.scope)

if __name__ == '__main__':
    main()
    print()

    
