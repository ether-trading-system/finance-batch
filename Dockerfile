FROM python:3.11

WORKDIR /finance-batch

RUN pip install poetry

COPY . .

RUN poetry install --no-root --no-interaction --no-cache --without dev

CMD [ "poetry", "run", "python", "main.py", ${period} ]