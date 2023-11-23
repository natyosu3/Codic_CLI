import argparse
import requests
import yaml
from pathlib import Path
import os, sys

config_path = Path(os.path.abspath(sys.argv[0])).parent.parent / "config" / "config.yaml"

parser = argparse.ArgumentParser(
    prog="cordic",
    description="cordicのCLIです."
)
parser.add_argument("text", help="変換したいテキストを入力してください.", type=str, default=None, nargs="?")
parser.add_argument("-a", "--api_token", help="codicのapiキーを設定してください.")
args = parser.parse_args()


def check_config_existence(func):
    def wrapper(*args, **kwargs):
        if not(os.path.isfile(config_path)):
            print("configuration file Not Found.")
            print("Create configuration directory...")
            if os.mkdir(Path(os.path.abspath(sys.argv[0])).parent.parent / "config"): print("Success.")
            else:
                print("Error. Could not create configuration directory.")
                sys.exit()
            
            print("Create configuration file...")
            try:
                with open(config_path, "w") as f:
                    f.write(yaml.safe_dump({"API_TOKEN": None,
                                            "DEFAULT_CASING": "lower underscore"
                                            }))
            except:
                print("Error. Could not create configuration file")
                sys.exit()
            print("Success.")

        return func(*args, **kwargs)
    return wrapper


@check_config_existence
def load_api_token():
    with open(config_path, "r") as f:
        API_TOKEN = yaml.safe_load(f)["API_TOKEN"]

    if API_TOKEN:
        return API_TOKEN
    else:
        print("API TOKENが設定されていません. 以下のコマンドを実行し, TOKENを設定してください.")
        print("cordic -a xxxxxx(API TOKEN)")
        sys.exit()


@check_config_existence
def load_default_casing():
    with open(config_path, "r") as f:
        DEFAULT_CASING = yaml.safe_load(f)["DEFAULT_CASING"]

    if DEFAULT_CASING:
        return DEFAULT_CASING


@check_config_existence
def api(text):
    url = "https://api.codic.jp/v1/engine/translate.json"
    headers = {
        "Authorization": f"Bearer {load_api_token()}"
    }

    payload = {
        "text": text,
        "casing": "lower underscore"
    }
    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        result = response.json()
        print(result[0]['translated_text'])
    else:
        print(f"Error: {response.status_code} - {response.text}")

@check_config_existence
def set_api_token(token):
    with open(config_path, "r+") as f:
        data = yaml.safe_load(f.read)
        data["API_TOKEN"] = token
        f.write(yaml.safe_dump(data))


if args.api_token: set_api_token(args.api_token)

if args.text: api(args.text)
else: parser.print_help()
