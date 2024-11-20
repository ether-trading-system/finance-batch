import requests as rq  # requests 라이브러리를 rq로 축약하여 가져오기
from bs4 import BeautifulSoup  # BeautifulSoup 라이브러리 가져오기 (HTML 파싱에 사용)

# 네이버 금융에서 예수금 데이터를 가져오기 위한 URL 설정
url = 'https://finance.naver.com/sise/sise_deposit.nhn'
data = rq.get(url)  # URL로 HTTP GET 요청 보내기
data_html = BeautifulSoup(data.content, features="html.parser")  # 응답 데이터를 BeautifulSoup으로 파싱

# 페이지에서 기준 날짜를 가져오기 위한 CSS 선택자 활용
parse_day = data_html.select_one('div.subtop_sise_graph2 > ul.subtop_chart_note > li > span.tah').text

import re  # 정규 표현식 라이브러리 가져오기

print(parse_day)  # 파싱된 기준 날짜 출력

# 기준 날짜에서 숫자만 추출 (YYYYMMDD 형식으로 변환)
biz_day = re.findall('[0-9]+', parse_day)  # 숫자만 추출
biz_day = ''.join(biz_day)  # 리스트를 문자열로 병합

print(biz_day)  # 변환된 기준 날짜 출력

import requests as rq  # 다시 requests 가져오기 (이미 위에서 import했으므로 필요 없음)
from io import BytesIO  # 바이트 데이터를 파일처럼 다룰 수 있는 BytesIO 가져오기
import pandas as pd  # 데이터 처리를 위한 pandas 라이브러리 가져오기

# 코스피 데이터 수집 시작
gen_otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'  # OTP 생성 URL 설정
gen_otp_stk = {  # 코스피 데이터를 요청하기 위한 매개변수
    'mktId': 'STK',  # 시장 ID: 코스피
    'trdDd': biz_day,  # 기준 거래일
    'money': '1',  # 데이터 형식
    'csvxls_isNo': 'false',  # CSV 형식으로 데이터 요청
    'name': 'fileDown',  # 요청 이름
    'url': 'dbms/MDC/STAT/standard/MDCSTAT03901'  # 데이터 URL
}

# HTTP 요청 헤더 설정
headers = {'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'}

otp_stk = rq.post(gen_otp_url, gen_otp_stk, headers=headers).text  # OTP 생성 요청 및 응답
print(otp_stk)  # 생성된 OTP 출력

# 생성된 OTP로 코스피 데이터를 다운로드
down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
down_sector_stk = rq.post(down_url, {'code': otp_stk}, headers=headers)

sector_stk = pd.read_csv(BytesIO(down_sector_stk.content), encoding='EUC-KR')  # 데이터 읽기

# 코스닥 데이터 수집 시작
gen_otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
gen_otp_ksq = {  # 코스닥 데이터를 요청하기 위한 매개변수
    'mktId': 'KSQ',  # 시장 ID: 코스닥
    'trdDd': biz_day,  # 기준 거래일
    'money': '1',
    'csvxls_isNo': 'false',
    'name': 'fileDown',
    'url': 'dbms/MDC/STAT/standard/MDCSTAT03901'
}

otp_ksq = rq.post(gen_otp_url, gen_otp_ksq, headers=headers).text  # OTP 생성 요청
down_sector_ksq = rq.post(down_url, {'code': otp_ksq}, headers=headers)  # 데이터 다운로드

sector_ksq = pd.read_csv(BytesIO(down_sector_ksq.content), encoding='EUC-KR')  # 데이터 읽기
print(sector_ksq)  # 코스닥 데이터 출력

# 코스피와 코스닥 데이터를 하나의 DataFrame으로 결합
krx_sector = pd.concat([sector_stk, sector_ksq]).reset_index(drop=True)
krx_sector['종목명'] = krx_sector['종목명'].str.strip()  # 종목명 공백 제거
krx_sector['기준일'] = biz_day  # 기준일 추가

# 개별 종목 데이터 수집
gen_otp_data = {  # 개별 종목 데이터를 요청하기 위한 매개변수
    'searchType': '1',
    'mktId': 'ALL',  # 모든 시장
    'trdDd': biz_day,  # 기준 거래일
    'money': '1',
    'csvxls_isNo': 'false',
    'name': 'fileDown',
    'url': 'dbms/MDC/STAT/standard/MDCSTAT03501'
}

otp_data = rq.post(gen_otp_url, gen_otp_data, headers=headers).text  # OTP 생성
krx_ind = rq.post(down_url, {'code': otp_data}, headers=headers)  # 데이터 다운로드

krx_ind = pd.read_csv(BytesIO(krx_ind.content), encoding='EUC-KR')  # 데이터 읽기
krx_sector['종목명'] = krx_sector['종목명'].str.strip()  # 종목명 공백 제거
krx_sector['기준일'] = biz_day  # 기준일 추가

# 데이터 비교 및 병합
set(krx_sector['종목명']).symmetric_difference(set(krx_ind['종목명']))  # 종목명 차집합 구하기

kor_ticker = pd.merge(krx_sector,
                      krx_ind,
                      on=krx_sector.columns.intersection(krx_ind.columns).tolist(),
                      how='outer')  # 두 데이터를 병합

print("KRX Sector DataFrame:")
print(krx_sector.head())
print("Kor Ticker DataFrame:")
print(kor_ticker.head())

# 조건별 종목 구분 추가 (스팩, 우선주, 리츠 등)
import numpy as np  # 수치 계산 라이브러리 가져오기

diff = list(set(krx_sector['종목명']).symmetric_difference(set(krx_ind['종목명'])))  # 종목명 차집합

kor_ticker['종목구분'] = np.where(kor_ticker['종목명'].str.contains('스팩|제[0-9]+호'), '스팩',
                              np.where(kor_ticker['종목코드'].str[-1:] != '0', '우선주',
                                       np.where(kor_ticker['종목명'].str.endswith('리츠'), '리츠',
                                                np.where(kor_ticker['종목명'].isin(diff), '기타',
                                                         '보통주'))))

# 최종 데이터 정리
kor_ticker = kor_ticker.reset_index(drop=True)
kor_ticker.columns = kor_ticker.columns.str.replace(' ', '')  # 컬럼명 공백 제거
kor_ticker = kor_ticker[['종목코드', '종목명', '시장구분', '종가', '시가총액', '기준일', 'EPS', '선행EPS', 'BPS', '주당배당금', '종목구분']]
kor_ticker = kor_ticker.replace({np.nan: None})  # NaN 값을 None으로 대체

print(kor_ticker[kor_ticker['종목명'] == '유비쿼스 [락]'])

kor_ticker = kor_ticker[kor_ticker['종목명'] != '유비쿼스 [락]']

# PostgreSQL 데이터베이스에 저장
import psycopg2  # PostgreSQL 데이터베이스 연결 라이브러리 가져오기

# 데이터 크롤링 및 PostgreSQL에 삽입 실행
conn_params = {
    'dbname': 'postgres',
    'user': 'finance',
    'password': 'finance',
    'host': 'postgres.whgusqls007.site',
    'port': '9999'
}

conn = psycopg2.connect(**conn_params)  # PostgreSQL 연결
mycursor = conn.cursor()  # 커서 객체 생성

# 데이터 삽입 쿼리 작성 (충돌 시 업데이트)
query = """
INSERT INTO kor_ticker (종목코드, 종목명, 시장구분, 종가, 시가총액, 기준일, EPS, 선행EPS, BPS, 주당배당금, 종목구분)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (종목코드,기준일) 
DO UPDATE SET 
종목명 = EXCLUDED.종목명,
시장구분 = EXCLUDED.시장구분,
종가 = EXCLUDED.종가,
시가총액 = EXCLUDED.시가총액,
기준일 = EXCLUDED.기준일,
EPS = EXCLUDED.EPS,
선행EPS = EXCLUDED.선행EPS,
BPS = EXCLUDED.BPS,
주당배당금 = EXCLUDED.주당배당금,
종목구분 = EXCLUDED.종목구분;
    """

args = kor_ticker.values.tolist()  # DataFrame을 리스트로 변환
mycursor.executemany(query, args)  # 쿼리 실행
conn.commit()  # 트랜잭션 커밋
mycursor.close()  # 커서 닫기
conn.close()  # 연결 종료
