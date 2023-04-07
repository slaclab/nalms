FROM alpine:3.17

RUN apk add --no-cache bash tzdata python3 py3-pip

ENV TZ=America/Los_Angeles

RUN pip3 install kafka-python

COPY alarm_logger.py /alarm_logger.py

ENTRYPOINT ["python3", "/alarm_logger.py"]
