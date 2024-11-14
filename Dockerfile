FROM python:3.11 as python-base

WORKDIR /finance-batch

RUN pip install poetry

COPY . .

RUN poetry install --no-root

ENTRYPOINT [ "poetry", "run", "python3", "main.py", ${period} ]
