FROM ghcr.io/linuxserver/baseimage-alpine:3.20

# set version label
LABEL maintainer="ozpinbeacon"

RUN \
  echo "**** install runtime packages ****" && \
  apk add --no-cache \
    py3-apscheduler \
    py3-flask \
    py3-ldap3 \
    py3-sqlalchemy \
    python3

# copy local files
COPY root/ /

# ports and volumes
VOLUME /config
