FROM ubuntu:latest
MAINTAINER Alex Hirschfeld <alex@d-qoi.com>

WORKDIR /root
RUN mkdir /mountpoint
VOLUME /mountpoint
COPY startUserProgram.sh /bin/startUserProgram.sh

CMD startUserProgram.sh
