import psycopg2  # PostgreSQL 데이터베이스 연결 라이브러리 가져오기

# 데이터베이스 연결 설정
conn_params = {
    'dbname': 'postgres',
    'user': 'finance',
    'password': 'finance',
    'host': 'postgres.whgusqls007.site',
    'port': '9999'
}

# PostgreSQL 연결
conn = psycopg2.connect(**conn_params)
mycursor = conn.cursor()  # 커서 객체 생성

# kor_ticker 테이블에서 code 조회
query = "SELECT 종목코드, 종목명 FROM kor_ticker WHERE 종목구분 = '보통주';"  # 조회 쿼리 작성
mycursor.execute(query)  # 쿼리 실행

# 조회 결과 가져오기
tickers = {code: name for code, name in mycursor.fetchall()}  # 딕셔너리 형태로 저장

# 전체 건수 출력
print(f"Total tickers: {len(tickers)}")

# 각 code 출력
for code in tickers:
    print(code)  # code 출력

# 전체 건수 출력
print(f"Total tickers: {len(tickers)}")

# 커서와 연결 닫기
mycursor.close()
conn.close()

#from temp.get_yearly_data import get_fnguide_table
#get_fnguide_table(tickers)

#term="year"
term="quarter"
from batch.get_finance_data import GetFinanceData
FinanceBatch = GetFinanceData(term=term)
#tickers = {
#    "005930": "삼성전자",  # 005930: 삼성전자 티커
#    "088980": "맥쿼리인프라"    # 066570: LG전자 티커
#}
data = FinanceBatch.getFinanceData(tickers)
FinanceBatch.insertDB(df=data, term=term)