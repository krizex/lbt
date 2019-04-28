FROM ubuntu:18.04 as builder
RUN apt update \
    && apt install -y wget \
    && apt install -y build-essential


# install ta-lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && tar xzvf ta-lib-0.4.0-src.tar.gz && cd ta-lib && mkdir /usr-tmp && ./configure --prefix=/usr-tmp && make && make install

# --------------------
FROM ubuntu:18.04
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ARG persist

RUN apt update
# install Python3
RUN apt install -y python3-pip python3-dev \
    && cd /usr/local/bin \
    && ln -s /usr/bin/python3 python \
    && pip3 install --upgrade pip

RUN apt install -y build-essential
RUN apt install -y python-dev

# install ta-lib
COPY --from=builder /usr-tmp /usr
ENV LD_LIBRARY_PATH /usr/lib

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN rm -f requirements.txt

COPY src/ /app/
COPY ${persist} /persist/
WORKDIR /app
EXPOSE 8000

CMD ./server.sh start
