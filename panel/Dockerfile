FROM python:3.8.6

RUN mkdir /app

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

CMD ["python3", "-u", "main.py"]