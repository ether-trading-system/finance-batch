import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from bs4.element import ResultSet
from batch.finance_db import FinanceDB


# 추후 ticker로 함께 관리
tickers = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "005490": "POSCO",
    "034730": "SK",
    "105560": "KB금융",
    "035420": "NAVER",
    "055550": "신한지주",
}


class GetFinanceData(FinanceDB):
    def __init__(self, term: str = "year") -> None:
        super().__init__()
        self.term = term
        self.desired_columns = [
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

    def htmlParser(self, code: str) -> tuple[ResultSet, ResultSet]:
        try:
            # URL 요청
            url = f"http://comp.fnguide.com/SVO2/ASP/SVD_main.asp?pGB=1&gicode=A{code}"
            response = requests.get(url)

            # HTTP 응답 상태 체크
            if response.status_code != 200:
                raise Exception(f"HTTP 요청 실패: {response.status_code}")

            # HTML 파싱
            soup = bs(response.content, "html.parser")

            # 재무정보 부분 탐색
            third_div = (
                soup.find("div", {"class": "fng_body asp_body"})
                .find("div", {"id": "div15"})
                .find(
                    "div",
                    {"id": "highlight_D_Y" if self.term == "year" else "highlight_D_Q"},
                )
            )

            # 재무정보가 없는 경우 처리
            if third_div is None:
                print(f"종목 {code}: 재무정보가 제공되지 않습니다.")
                return None, None

            # tbody와 thead 정보 추출
            parsed_html_tbody_tr = third_div.find("tbody").find_all("tr")
            parsed_html_thead_tr = (
                third_div.find("thead")
                .find("tr", {"class": "td_gapcolor2"})
                .find_all("th")
            )

            return parsed_html_tbody_tr, parsed_html_thead_tr

        except Exception as e:
            # 예외 발생 시 로그 출력 및 빈 데이터 반환
            print(f"Error processing {code}: {str(e)}")
            return None, None

    def getDataFromParsedHtml(
        self, parsed_html: tuple[ResultSet, ResultSet]
    ) -> tuple[dict, list]:
        
        if parsed_html is None:
            print("Error: 파싱된 HTML 데이터가 없습니다.")
            return []
        
        tbody_tr, thead_tr = parsed_html

        # tbody_tr 검증
        if tbody_tr is None or thead_tr is None:
            print("Error: tbody 또는 thead 데이터가 없습니다.")
            return [] 

        data = {}

        for row in tbody_tr:
            category = row.find("span", {"class": "txt_acd"})
            if category is None:
                category = row.find("th")
            category = category.text.strip()

            value_list = []
            cells = row.find_all("td", {"class": "r"})
            for cell in cells:  # 셀 순회
                temp = cell.text.replace(",", "").strip()
                try:
                    temp = float(temp)
                except:
                    temp = None
                value_list.append(temp)

            if category in self.desired_columns:
                data[category] = value_list

        year_list = []

        for th in thead_tr:
            try:
                temp_year = th.find("span", {"class": "txt_acd"}).text
            except:
                temp_year = th.text
            year_list.append(temp_year)

        return data, year_list

    def makeDataFrame(
        self, datas: tuple[dict, list], code: str, name: str
    ) -> pd.DataFrame:
        data, list = datas

        Table = pd.DataFrame(data, index=list)
        Table.index.name = "연도"

        Table["종목코드"] = code
        Table["종목명"] = name

        Table = Table.reset_index()
        Table = Table[
            ["연도", "종목코드", "종목명"]
            + [col for col in self.desired_columns if col in Table.columns]
        ]
        return Table

    def getFinanceData(self, tickers):
        datas = []

        for code, name in tickers.items():
            parsed_html = self.htmlParser(code=code)
            data = self.getDataFromParsedHtml(parsed_html=parsed_html)

            if not data:  # data가 None 또는 빈 리스트인 경우
                print(f"종목 {code}의 재무정보가 없습니다. 빈 데이터프레임 생성.")
                datas.append(pd.DataFrame())  # 빈 데이터프레임 추가
                continue  # 다음 종목으로 넘어감
            
            df = self.makeDataFrame(datas=data, code=code, name=name)
            datas.append(df)

        df = pd.concat(datas, ignore_index=True)
        return df
