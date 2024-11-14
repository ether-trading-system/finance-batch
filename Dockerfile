FROM python:3.11 as builder

RUN pip install poetry

WORKDIR /finance-batch

COPY . .

RUN poetry install --no-root

RUN poetry shell

CMD ["poetry", "run", "python", "main.py", "year"]
