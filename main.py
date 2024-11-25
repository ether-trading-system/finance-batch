import sys

from batch.get_finance_data import GetFinanceData

if __name__ == "__main__":
    term = ""
    try:
        term = sys.argv[1]
    except:
        print("Startup parameter are required (year, quarter)")
        exit

    print(f"{term}ly Batch Start")

    FinanceBatch = GetFinanceData(term=term)
    data = FinanceBatch.getFinanceData()
    FinanceBatch.insertDB(df=data, term=term)
