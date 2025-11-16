FROM python:3.11.11

RUN apt-get update
RUN apt-get install ffmpeg -y

COPY --from=denoland/deno:bin-2.5.6 /deno /usr/local/bin/deno
RUN python --version && deno --version

WORKDIR /app
ADD requirements.txt .
RUN pip3 install -r requirements.txt

ADD ./cogs ./cogs
ADD ./objects ./objects
ADD ./main.py .
ADD ./.env .
ADD ./cookies.txt .

CMD ["python3", "main.py"]
