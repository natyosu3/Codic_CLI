import argparse
import requests
import yaml
from pathlib import Path
import os, sys

config_path = Path(__file__).parent.parent / "config" / "config.yaml"

parser = argparse.ArgumentParser(
    prog="cordic",
    description="cordicのCLIです."
)
parser.add_argument("text", help="変換したいテキストを入力してください.", type=str, default=None)
parser.add_argument("-a", "--api_token", help="codicのapiキーを設定してください.")
args = parser.parse_args()


def load_api_token():
    if os.path.isfile(config_path):
        with open(config_path, "r") as f:
            API_TOKEN = yaml.safe_load(f)["API_TOKEN"]
        if API_TOKEN:
            return API_TOKEN

        else:
            print("API TOKENが設定されていません. 以下のコマンドを実行し, TOKENを設定してください.")
            print("cordic -a xxxxxx(API TOKEN)")
            sys.exit()

    else:
        with open(config_path, "w") as f:
            f.write(yaml.safe_dump({"API_TOKEN": None,
                                    "DEFAULT_CASING": "snake"
                                    }))
        print("API TOKENが設定されていません. 以下のコマンドを実行し, TOKENを設定してください.")
        print("cordic -a xxxxxx(API TOKEN)")
        sys.exit()


def load_default_casing():
    if os.path.isfile(config_path):
        with open(config_path, "r") as f:
            DEFAULT_CASING = yaml.safe_load(f)["DEFAULT_CASING"]
        if DEFAULT_CASING:
            return DEFAULT_CASING

    else:
        with open(config_path, "w") as f:
            f.write(yaml.safe_dump({"API_TOKEN": None,
                                    "DEFAULT_CASING": "lower underscore"
                                    }))


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

# load_api_token()
api(args.text)
