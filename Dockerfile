FROM python

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app/ app/

ENTRYPOINT [ "fastapi", "dev", "app/main.py" ]