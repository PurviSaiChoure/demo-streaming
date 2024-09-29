FROM python:3.9.13-slim

COPY requirements.txt .

RUN set -ex; \
    pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_sm

# Copy resources
WORKDIR /
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

ADD python-producer.py .

CMD /wait-for-it.sh $ZOOKEEPER_SERVER -t 30 -- /wait-for-it.sh $KAFKA_SERVER -t 60 -- python -u python-producer.py
