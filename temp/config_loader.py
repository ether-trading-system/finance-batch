from datetime import datetime
import requests
import json
import yaml
import os
from pathlib import Path

base_dir = Path(__file__).resolve().parent
file_name = "config.yaml"
print(base_dir)

file_path = base_dir / file_name
print(file_path)

with open(file_path, "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)

APP_KEY = config.get("APP_KEY")
APP_SECRET = config.get("APP_SECRET")
ACCESS_TOKEN = None
URL_BASE = "https://openapivts.koreainvestment.com:29443"  # 모의투자

# 토큰 파일 경로
TOKEN_FILE = "token.json"


# Auth
def get_token():
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
    }
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))

    print("---------------------------")
    print(res.json()["access_token"])
    print("---------------------------")

    return res.json()["access_token"]


def save_token(token, date):
    """토큰과 날짜를 파일에 저장"""
    with open(TOKEN_FILE, "w") as file:
        json.dump({"token": token, "date": date}, file)


def load_token():
    """파일에서 토큰과 날짜를 불러옴"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as file:
            data = json.load(file)
        return data.get("token"), data.get("date")
    return None, None


def get_daily_token():
    """당일 토큰을 가져오거나 새로 생성"""
    today = datetime.now().strftime("%Y-%m-%d")

    # 토큰과 저장된 날짜 불러오기
    token, token_date = load_token()

    # 토큰이 없거나 날짜가 다르면 새로 생성
    if not token or token_date != today:
        token = get_token()
        save_token(token, today)
        print("새로운 토큰을 생성했습니다.")
    else:
        print("당일 토큰을 사용합니다.")

    return token
