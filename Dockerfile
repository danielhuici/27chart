FROM python:3.10

COPY . ./
RUN pip3 install pytube tweepy pydrive

CMD ["python3", "./main.py"]