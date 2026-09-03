FROM python:3.11-slim

WORKDIR /usr/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DBT_PROFILES_DIR=/usr/app

ENTRYPOINT ["dbt"]
CMD ["build"]
