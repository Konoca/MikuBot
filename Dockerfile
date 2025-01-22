FROM python:latest

RUN apt-get update
RUN apt-get install ffmpeg -y

WORKDIR /app
ADD requirements.txt .
RUN pip3 install -r requirements.txt

ADD ./cogs ./cogs
ADD ./objects ./objects
ADD ./main.py .
ADD ./.env .
ADD ./cookies.txt .

CMD ["python3", "main.py"]
