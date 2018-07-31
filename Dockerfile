
#Use an official linux and Python runtime as a parent image
FROM alpine:3.8

LABEL maintainer "Chris B & Pedro J <dev@pagarba.io>"
LABEL description "streamiot devices on blockchain"

# Copy python requirements file
COPY requirements.txt /tmp/requirements.txt

COPY . /app
WORKDIR /app

EXPOSE  5000


RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache
RUN pip3 install requests
RUN pip3 install --trusted-host pypi.python.org -r /tmp/requirements.txt
RUN apk update
RUN apk add nodejs
RUN apk add npm
RUN pip install Flask-Cors
RUN apk update
RUN npm install bitcore-mnemonic
RUN rm -r /tmp/requirements.txt
