from typing import Union
import uvicorn
from fastapi import FastAPI
from batch.current_price_samle import get_current_price

#서버실행방법, 터미널에서 우측 명령어 실행 uvicorn app.main:start
app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/current-price/")
def current_price(stock_code: str):
    """
    특정 배치 프로그램을 실행하고 그 결과를 반환하는 API 엔드포인트
    """
    result = get_current_price(stock_code)
    
    return {"result": result}

def start():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)