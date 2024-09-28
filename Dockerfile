FROM ubuntu:latest

WORKDIR /root/27chart

COPY . .
RUN apt update -y
RUN apt install -y python3 python3-pip ffmpeg libpq-dev python3-dev git python3-venv postgresql-client chrome
RUN pip3 install -r requeriments.txt

CMD ["python3", "main.py"]
