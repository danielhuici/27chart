FROM ubuntu:latest

WORKDIR /root/27chart

COPY . .
RUN apt update -y
RUN apt install -y python3 python3-pip ffmpeg libpq-dev python3-dev git
RUN pip3 install git+https://github.com/dudegladiator/pytube.git tweepy pydrive yt_dlp psycopg2 pexpect

CMD ["python3", "main.py"]
