FROM  ubuntu:latest

WORKDIR /root/27chart

COPY . .
RUN apt update -y
RUN apt install -y python3 python3-pip ffmpeg libpq-dev python3-dev git python3-venv postgresql-common
RUN /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -i -v 17
RUN apt install -y postgresql-client-17
RUN pip install --break-system-packages -r requirements.txt

CMD ["python3", "main.py"]
