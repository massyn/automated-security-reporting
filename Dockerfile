FROM python:3

WORKDIR /python-docker

RUN apt-get update
RUN apt-get upgrade -y

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY 01-collectors  01-collectors
COPY 02-metrics     02-metrics

# === Core stuff ===
COPY run.sh 	.
RUN chmod +x *.sh
RUN mkdir data

CMD [ "sh" , "./run.sh"]
