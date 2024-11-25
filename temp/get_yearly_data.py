import requests  # 웹 요청을 보내기 위해 사용되는 라이브러리
from bs4 import BeautifulSoup  # HTML 파싱을 위한 라이브러리
import pandas as pd  # 데이터프레임 처리를 위한 라이브러리
import psycopg2  # PostgreSQL 데이터베이스 연결 및 작업을 위한 라이브러리
from psycopg2 import sql  # SQL 쿼리문 생성 및 안전한 처리에 사용

# 종목 코드와 기업명 정의 (주식 종목 코드와 그에 해당하는 기업명)
tickers = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "005490": "POSCO",
    "034730": "SK",
    "105560": "KB금융",
    "035420": "NAVER",
    "055550": "신한지주",
}

# 원하는 항목 목록 정의 (수집할 재무 데이터의 항목명 리스트)
desired_columns = [
    "매출액",
    "영업이익",
    "영업이익(발표기준)",
    "당기순이익",
    "지배주주순이익",
    "비지배주주순이익",
    "자산총계",
    "부채총계",
    "자본총계",
    "지배주주지분",
    "비지배주주지분",
    "자본금",
    "부채비율",
    "유보율",
    "영업이익률",
    "지배주주순이익률",
    "ROA",
    "ROE",
    "EPS",
    "BPS",
    "DPS",
    "PER",
    "PBR",
    "발행주식수",
    "배당수익률",
]


# FnGuide에서 재무 데이터를 크롤링하는 함수 정의
def get_fnguide_table(tickers):
    all_data = []  # 모든 종목의 데이터를 저장할 리스트 초기화

    for code, name in tickers.items():  # 각 종목 코드와 기업명을 순회
        # 특정 종목의 FnGuide URL에 HTTP 요청 보내기
        url = requests.get(
            f"http://comp.fnguide.com/SVO2/ASP/SVD_main.asp?pGB=1&gicode=A{code}"
        )
        html = BeautifulSoup(url.content, "html.parser")  # HTML 파싱

        # 필요한 재무 데이터 테이블이 있는 div 태그 찾기
        fn_body = html.find("div", {"class": "fng_body asp_body"})
        ur_table = fn_body.find("div", {"id": "div15"})
        table = ur_table.find("div", {"id": "highlight_D_Y"})

        tbody = table.find("tbody")  # 테이블의 본문 부분을 찾기
        tr = tbody.find_all("tr")  # 모든 행 가져오기

        data = {}  # 각 항목의 데이터를 저장할 딕셔너리 초기화

        for row in tr:  # 테이블의 각 행을 순회
            category = row.find("span", {"class": "txt_acd"})  # 항목명 찾기
            if category is None:  # 항목명이 span 태그에 없을 경우 th 태그에서 찾기
                category = row.find("th")
            category = category.text.strip()  # 텍스트로 변환하고 앞뒤 공백 제거

            value_list = []  # 각 항목의 값을 저장할 리스트 초기화
            cells = row.find_all("td", {"class": "r"})  # 행의 모든 셀 가져오기
            for cell in cells:  # 셀 순회
                temp = cell.text.replace(",", "").strip()  # 쉼표 제거 및 공백 제거
                try:
                    temp = float(temp)  # 숫자로 변환 시도
                except:
                    temp = None  # 변환 실패 시 None으로 설정
                value_list.append(temp)  # 리스트에 값 추가

            if category in desired_columns:  # 항목이 원하는 컬럼 목록에 있으면 추가
                data[category] = value_list

        thead = table.find("thead")  # 테이블의 헤더 부분 찾기
        tr_2 = thead.find("tr", {"class": "td_gapcolor2"}).find_all(
            "th"
        )  # 헤더 행의 모든 열 가져오기
        year_list = []  # 연도 리스트 초기화

        for th in tr_2:  # 헤더의 각 열을 순회
            try:
                temp_year = th.find(
                    "span", {"class": "txt_acd"}
                ).text  # 연도 텍스트 가져오기
            except:
                temp_year = th.text  # 연도 텍스트가 없으면 기본 텍스트로 설정
            year_list.append(temp_year)  # 연도 리스트에 추가

        # 데이터프레임 생성 및 데이터 정리
        Table = pd.DataFrame(data, index=year_list)  # 연도를 인덱스로 데이터프레임 생성
        Table.index.name = "연도"  # 인덱스 이름 설정

        Table["종목코드"] = code  # 종목코드 추가
        Table["종목명"] = name  # 종목명 추가

        # 컬럼 순서 조정
        Table = Table.reset_index()  # 인덱스 리셋
        Table = Table[
            ["연도", "종목코드", "종목명"]
            + [col for col in desired_columns if col in Table.columns]
        ]  # 열 순서 재정렬

        # 빈 데이터프레임이나 모든 값이 NaN인 경우 제외
        if not Table.empty and not Table.isna().all().all():
            all_data.append(Table)  # 유효한 데이터프레임만 추가

    # 병합 수행
    if all_data:  # all_data가 비어 있지 않다면 병합
        final_df = pd.concat(all_data, ignore_index=True)
    else:  # 비어 있다면 빈 데이터프레임 반환
        final_df = pd.DataFrame()

    return final_df  # 최종 데이터프레임 반환


# 데이터프레임을 PostgreSQL 테이블에 삽입하는 함수 정의
def insert_data_to_postgresql(df, conn_params):
    conn = psycopg2.connect(**conn_params)  # PostgreSQL 연결
    cursor = conn.cursor()  # 커서 객체 생성

    # 안전한 SQL 쿼리 작성
    insert_query = sql.SQL(
        """
        INSERT INTO financial_data (
            year, ticker_code, company_name, revenue, operating_profit, 
            reported_operating_profit, net_income, controlling_shareholder_net_income, 
            non_controlling_interest_net_income, total_assets, total_liabilities, 
            total_equity, controlling_shareholder_equity, non_controlling_interest_equity, 
            capital_stock, debt_ratio, retention_ratio, operating_margin, 
            controlling_shareholder_net_margin, roa, roe, eps, bps, dps, per, 
            pbr, shares_outstanding, dividend_yield
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (year, ticker_code) DO NOTHING;  -- 중복된 기본 키가 있으면 삽입 무시
    """
    )

    for _, row in df.iterrows():  # 데이터프레임의 각 행을 순회
        cursor.execute(insert_query, tuple(row))  # SQL 쿼리 실행 및 행 삽입

    conn.commit()  # 트랜잭션 커밋
    cursor.close()  # 커서 닫기
    conn.close()  # 연결 종료


# 데이터 크롤링 및 PostgreSQL에 삽입 실행
conn_params = {
    "dbname": "postgres",
    "user": "finance",
    "password": "finance",
    "host": "postgres.whgusqls007.site",
    "port": "9999",
}

final_df = get_fnguide_table(tickers)  # 데이터 크롤링 및 데이터프레임 z
insert_data_to_postgresql(final_df, conn_params)  # 데이터프레임을 PostgreSQL에 삽입
