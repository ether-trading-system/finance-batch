import requests
import json
from batch.config_loader import APP_KEY
from batch.config_loader import APP_SECRET
from batch.config_loader import URL_BASE
from batch.config_loader import get_daily_token

# 주식현재가 시세
def get_current_price(stock_no):
    PATH = "uapi/domestic-stock/v1/quotations/inquire-price"
    URL = f"{URL_BASE}/{PATH}"
    
    # 헤더 설정
    headers = {"Content-Type":"application/json",
            "authorization": f"Bearer {get_daily_token()}",
            "appKey":APP_KEY,
            "appSecret":APP_SECRET,
            "tr_id":"FHKST01010100"}

    params = {
        "fid_cond_mrkt_div_code":"J",
        "fid_input_iscd": stock_no
    }

    # 호출
    res = requests.get(URL, headers=headers, params=params)

    # 응답을 JSON으로 변환
    data = res.json()
    json_str = json.loads(json.dumps(data))
    print(json_str["output"]["stck_prpr"])

    # JSON 데이터를 pretty하게 출력
    pretty_json = json.dumps(data, indent=4, ensure_ascii=False)
    print(pretty_json)

    if res.status_code == 200 and res.json()["rt_cd"] == "0" :
        return(res.json())
    # 토큰 만료 시
    #elif res.status_code == 200 and res.json()["msg_cd"] == "EGW00123" :
    #    get_current_price(stock_no)
    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return None

get_current_price("005930")

