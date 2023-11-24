import argparse
from argparse import RawTextHelpFormatter
import requests
import yaml
from pathlib import Path
import os, sys

config_dir = Path(os.path.abspath(sys.argv[0])).parent.parent / "config"
config_path = config_dir / "config.yaml"

parser = argparse.ArgumentParser(
    prog="coc",
    description="cordicのCLIです.",
    formatter_class=RawTextHelpFormatter
)
parser.add_argument("text", help="変換したいテキストを入力してください.", type=str, default=None, nargs="?")
parser.add_argument("-a", "--api_token", help="codicのapiキーを設定してください.")
parser.add_argument("-c", "--casing", help="""
                    利用したいケーシングを入力してください.
                    lower underscore: hello_func
                    upper underscore: HELLO_FUNC
                    camel           : helloFunc
                    pascal          : HelloFunc
                    hyphen          : hello-func
                    """)
parser.add_argument("-cdc", "--change_default_casing", help="デフォルトのケーシングを変更します.")
args = parser.parse_args()


def check_config_existence(func):
    def wrapper(*args, **kwargs):
        if not(os.path.isfile(config_path)):
            print("configuration file Not Found. Creating...")

            if not config_dir.is_dir():
                try:
                    config_dir.mkdir(parents=True, exist_ok=True)
                    print("Configuration directory created successfully.")
                except Exception as e:
                    print(f"Error creating configuration directory: {e}")
                    sys.exit()
            
            try:
                with open(config_path, "w") as f:
                    yaml.safe_dump(stream=f, data={"API_TOKEN": None,
                                            "DEFAULT_CASING": "lower underscore"
                                            })
                print("Configuration file created successfully.")
            except Exception as e:
                print(f"Error creating configuration file: {e}")
                sys.exit()

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
        print("coc -a xxxxxx(API TOKEN)")
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
    casing = args.casing if args.casing else load_default_casing()

    headers = {
        "Authorization": f"Bearer {load_api_token()}"
    }

    payload = {
        "text": text,
        "casing": casing
    }
    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        result = response.json()
        print(result[0]['translated_text'])
    elif response.status_code == 401:
        print(f"ERROR. 認証に失敗しました. 正しいapi tokenを設定してください.")
        print("api token確認ページ -> https://codic.jp/my/api_status")
        print()
        print("-a オプションでapi tokenを設定してください.")
        print("ex: coc -a xxxxxxxx(api token)")
        sys.exit()
    else:
        error_msg = response.text.decode("unicode-escape")
        print(f"Error: {response.status_code} - {error_msg}")

@check_config_existence
def set_api_token(token):
    try:
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
        with open(config_path, "w") as f:
            data["API_TOKEN"] = token
            yaml.safe_dump(data, f)
        print("Success.")
        sys.exit()
    except Exception as e:
        print("Error. Can't set the api_token.", e)

@check_config_existence
def set_default_casing(casing):
    try:
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
        with open(config_path, "w") as f:
            data["DEFAULT_CASING"] = casing
            yaml.safe_dump(data, f)
        print("Success.")
        sys.exit()
    except Exception as e:
        print("Error. Can't set the default casing.", e)


if args.api_token: set_api_token(args.api_token)
if args.change_default_casing: set_default_casing(args.change_default_casing)

if args.text: api(args.text)
else: parser.print_help()