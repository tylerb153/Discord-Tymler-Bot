# syntax=docker/dockerfile:1

FROM python:3.13.8-slim

RUN apt-get update
RUN apt-get install -y libopus0 ffmpeg
# RUN apt-get update && apt-get install -y openssh-client

RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY . .

RUN pip3 install -r requirements.txt

# RUN pip uninstall -y "discord.py"
# # RUN apt install git -y
# # RUN pip install "git+https://github.com/Rapptz/discord.py@master"

CMD ["python3", "bot.py"]