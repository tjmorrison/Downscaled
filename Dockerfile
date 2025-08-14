FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libboost-all-dev \
    libxml2-dev \
    libbz2-dev \
    libproj-dev \
    libgdal-dev \
    wget

WORKDIR /opt

COPY ./meteoio-master /opt/meteoio
COPY ./snowpack-master /opt/snowpack

RUN mkdir /opt/meteoio/build && cd /opt/meteoio/build && \
    cmake .. && make -j$(nproc) && make install

RUN mkdir /opt/snowpack/build && cd /opt/snowpack/build && \
    cmake .. && make -j$(nproc) && make install

ENV PATH="/usr/local/bin:${PATH}"

WORKDIR /data
CMD ["bash"]
