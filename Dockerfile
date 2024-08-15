FROM ghcr.io/imagegenius/baseimage-alpine:3.20

# set version label
LABEL maintainer="ozpinbeacon"

RUN \
  echo "**** install runtime packages ****" && \
  apk add --no-cache \
	python3 \
		python3-flask \
		python3-datetime \
		python3-apscheduler \
		python3-ldap3 \
		python3-sqlite3

# copy local files
COPY root/ /

# Set environmental variables
ENV FLASK_APP=ADOverseas

# Execute the service
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "3500"]



