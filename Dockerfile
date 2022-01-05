FROM python:3-alpine

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir /config

ADD app.py .

CMD ["python3", "-u", "app.py"]