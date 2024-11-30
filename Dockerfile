FROM python:3

WORKDIR /python-docker

RUN apt-get update
RUN apt-get upgrade -y

# == Install AWS Cli
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-$(uname -m).zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm awscliv2.zip

# == web stuff
RUN apt-get install lighttpd lighttpd-doc -y
COPY 03-dashboard/build /var/www/html
COPY lighttpd.conf /etc/lighttpd/lighttpd.conf

# == install the main app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY 01-collectors  01-collectors
COPY 02-metrics     02-metrics

# === Core stuff ===
COPY main.sh .
COPY run.sh  .
RUN chmod +x *.sh
RUN mkdir data

EXPOSE 8081

CMD [ "sh" , "./main.sh"]
