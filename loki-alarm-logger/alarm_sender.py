import argparse
import json
import logging
import os
import requests
from datetime import datetime, timedelta
from kafka import KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord
from typing import List

logging.basicConfig(level=logging.INFO, format='%(message)s')


class AlarmSender:
    """
    AlarmSender is a simple process for reading message from kafka topics and sending them to a slack channel

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
        self.descriptions = dict()
        self.main_consumer = KafkaConsumer(*topics,
                                           bootstrap_servers=bootstrap_servers,
                                           auto_offset_reset='earliest',
                                           enable_auto_commit=False,
                                           key_deserializer=lambda x: x.decode('utf-8'),
                                           value_deserializer=self.value_decode)

    def value_decode(self, x):
        if x is not None:
            return json.loads(x.decode('utf-8'))
        return None

    def run(self):
        url = os.getenv("SLACK_WEBHOOK_URL")
        headers = {"Content-type": "application/json"}
        data = {"text": ""}

        # Read new alarm messages from Kafka as soon as they arrive
        for message in self.main_consumer:
            try:
                key = message.key
                if key.startswith('config'):
                    pv = message.key.split('/')[-1]
                    description = message.value.get('description', '')
                    self.descriptions[pv] = description
                elif message.value is not None and len(message.value) > 1:
                    message.value['pv_name'] = message.key.split('/')[-1]
                    if 'severity' in message.value:
                        # This is likely a duplicate message from a multiple alarm server setup, don't send again
                        if self.current_alarms.get(message.key) == message.value['severity']:
                            continue
                        self.current_alarms[message.key] = message.value['severity']

                        if ':' not in message.value['pv_name']:
                            continue

                        if 'time' in message.value:
                            time_of_alarm = datetime.fromtimestamp(message.value['time']['seconds'])
                            message.value['time'] = str(time_of_alarm)
                        else:
                            print(f'Rejecting message due to no timestamp: {message.value}')
                            continue

                        if (message.value['severity'] != 'OK' and message.value['current_severity'] != 'OK' and 'ACK' not in message.value['severity']):
                            # If this script was recently restarted, don't send out repeat alarms
                            # (Could also just not read from start of queue, but works better for the k8s use case)
                            one_minute_ago = datetime.now() - timedelta(minutes=1)
                            if time_of_alarm < one_minute_ago:
                                logging.info(f'Rejecting message due to being too old: {message.value} while cutoff was: {one_minute_ago}')
                                continue
                            data["text"] = f"```{message.value['pv_name']}     Severity: {message.value['severity']}     Message: {message.value.get('message', '')}      Description: {self.descriptions.get(message.value['pv_name'], '')}```"
                            response = requests.post(url, headers=headers, json=data)
            except Exception as e:
                logging.error(f"Error processing message: {e}")



def main():
    parser = argparse.ArgumentParser(description="Alarm Sender")
    parser.add_argument('--topics', help='Comma separated list of kafka alarm topics to listen to')
    parser.add_argument('--bootstrap-servers',
                        default='localhost:9092',
                        help='Comma separated list of urls for one or more kafka boostrap servers')

    app_args = parser.parse_args()
    topics = app_args.topics.split(',')
    kafka_boostrap_servers = app_args.bootstrap_servers.split(',')

    kafka_consumer = AlarmSender(topics, kafka_boostrap_servers)
    kafka_consumer.run()


if __name__ == '__main__':
    main()
