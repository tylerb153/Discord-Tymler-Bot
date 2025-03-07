# syntax=docker/dockerfile:1

FROM ubuntu:24.04

RUN apt-get update && apt-get install -y python3-pip
RUN apt-get install -y python3-venv
# RUN apt-get update && apt-get install -y openssh-client

RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY . .

RUN pip3 install -r requirements.txt

CMD ["python3", "bot.py"]