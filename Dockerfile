FROM ubuntu:latest

WORKDIR /root/27chart

COPY . .
RUN apt update -y
RUN apt install -y python3 python3-pip ffmpeg 
RUN pip3 install pytube tweepy pydrive yt_dlp

CMD ["python3", "main.py"]