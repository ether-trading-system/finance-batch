import pandas

from batch.env_loader import EnvLoader
from psycopg2 import connect
from psycopg2 import sql
from psycopg2.extensions import connection, cursor


class FinanceDB(EnvLoader):
    def __init__(self) -> None:
        super().__init__()
        self.conn = self.getConn()
        self.cursor = self.getCursor(self.conn)

    def __del__(self) -> None:
        self.conn.close()
        self.cursor.close()

    def getConn(self) -> connection:
        conn_params = self.getDBConnectionProperties()
        conn = connect(**conn_params)
        return conn

    def getCursor(self, conn: connection) -> cursor:
        cursor = conn.cursor()
        return cursor

    def insertDB(self, df: pandas.DataFrame, term: str = "") -> None:
        # query = f"INSERT INTO financial_data_{term}ly ({term}, ticker_code, company_name, revenue, operating_profit, reported_operating_profit, net_income, controlling_shareholder_net_income, non_controlling_interest_net_income, total_assets, total_liabilities, total_equity, controlling_shareholder_equity, non_controlling_interest_equity, capital_stock, debt_ratio, retention_ratio, operating_margin, controlling_shareholder_net_margin, roa, roe, eps, bps, dps, per, pbr, shares_outstanding, dividend_yield) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT ({term}, ticker_code) DO NOTHING;"
        query = self.getQUERY().format(term, term, term)
        insert_query = sql.SQL(query)

        for _, row in df.iterrows():
            self.cursor.execute(insert_query, tuple(row))

        self.conn.commit()
