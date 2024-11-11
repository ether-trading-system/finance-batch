import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from bs4.element import ResultSet
from batch.finance_db import FinanceDB

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


class GetFinanceData(FinanceDB):
    def __init__(self, term: str = "year") -> None:
        super().__init__()
        self.term = term

    def htmlParser(self, code: str) -> tuple[ResultSet, ResultSet]:
        url = requests.get(
            f"http://comp.fnguide.com/SVO2/ASP/SVD_main.asp?pGB=1&gicode=A{code}"
        )
        parsed_html_table = (
            bs(url.content, "html.parser")
            .find("div", {"class": "fng_body asp_body"})
            .find("div", {"id": "div15"})
            .find(
                "div",
                {"id": "highlight_D_Y" if self.term == "year" else "highlight_D_Q"},
            )
        )
        parsed_html_tbody_tr = parsed_html_table.find("tbody").find_all("tr")
        parsed_html_thead_tr = (
            parsed_html_table.find("thead")
            .find("tr", {"class": "td_gapcolor2"})
            .find_all("th")
        )

        return parsed_html_tbody_tr, parsed_html_thead_tr

    def getDataFromParsedHtml(
        self, parsed_html: tuple[ResultSet, ResultSet]
    ) -> tuple[dict, list]:
        tbody_tr, thead_tr = parsed_html

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

            if category in desired_columns:
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
            + [col for col in desired_columns if col in Table.columns]
        ]
        return Table

    def getFinanceData(self):
        datas = []

        for code, name in tickers.items():
            parsed_html = self.htmlParser(code=code)
            data = self.getDataFromParsedHtml(parsed_html=parsed_html)
            df = self.makeDataFrame(datas=data, code=code, name=name)
            datas.append(df)

        df = pd.concat(datas, ignore_index=True)
        return df
