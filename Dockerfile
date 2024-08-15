FROM ghcr.io/imagegenius/baseimage-alpine:3.20

# set version label
LABEL maintainer="ozpinbeacon"

RUN \
  echo "**** install runtime packages ****" && \
  apk add --no-cache \
	python3 \
		py3-flask \
		py3-sqlalchemy \
		py3-apscheduler \
		py3-ldap3 

# copy local files
COPY root/ /

# Execute the service
CMD ["flask", "--app", "ADOverseas", "run", "--host", "0.0.0.0", "--port", "3500"]



