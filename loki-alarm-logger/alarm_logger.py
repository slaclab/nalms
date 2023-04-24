import argparse
import json
import logging
from datetime import datetime
from kafka import KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord
from typing import List


logging.basicConfig(level=logging.INFO, format='%(message)s')


class AlarmLogger():
    """
    AlarmLogger is a simple class for reading message from kafka topics and logging them out to be
    processed by promtail -> loki.

    Parameters
    ----------
    topics : List[str]
        A list of topics representing the alarm configs to listen to
    bootstrap_servers : List[str]
        A list containing one or more urls for kafka bootstrap servers
    """

    def __init__(self, topics: List[str], bootstrap_servers: List[str]):
        self.topics = topics
        self.current_alarms = dict()
        self.main_consumer = KafkaConsumer(*topics,
                                           bootstrap_servers=bootstrap_servers,
                                           auto_offset_reset='latest',
                                           enable_auto_commit=False,
                                           key_deserializer=lambda x: x.decode('utf-8'),
                                           value_deserializer=self.value_decode)


    def value_decode(self, x):
        if x is not None:
            return json.loads(x.decode('utf-8'))
        return None

    def run(self):
        for message in self.main_consumer:
            if len(message.value) > 1:
                message.value['path'] = message.key
                message.value['pv_name'] = message.key.split('/')[-1]
                message.value['topic_name'] = message.key.split('/')[1]
                if 'severity' in message.value:
                    # This is likely a duplicate message from kafka, no need to log again
                    if self.current_alarms.get(message.key) == message.value['severity']:
                        continue
                    self.current_alarms[message.key] = message.value['severity']
                if 'time' in message.value:
                    message.value['time'] = str(datetime.fromtimestamp(message.value['time']['seconds']))
                logging.info(f'{json.dumps(message.value)}')


def main():
    parser = argparse.ArgumentParser(description="Alarm Logger")
    parser.add_argument('--topics', help='Comma separated list of kafka alarm topics to listen to')
    parser.add_argument('--bootstrap-servers',
                        default='localhost:9092',
                        help='Comma separated list of urls for one or more kafka boostrap servers')


    app_args = parser.parse_args()
    topics = app_args.topics.split(',')
    kafka_boostrap_servers = app_args.bootstrap_servers.split(',')
    

    kafka_consumer = AlarmLogger(topics, kafka_boostrap_servers)
    kafka_consumer.run()


if __name__ == '__main__':
    main()
