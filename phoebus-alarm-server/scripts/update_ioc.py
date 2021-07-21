from kafka import KafkaConsumer
import epics
import json

def monitor(config_name:str, kafka_bootstrap:str, retry_count:int=10):
    """Monitor Kafka topics and write to designated alarm process variables.

    Args:
        config_name (str): Name of configuration 
        kafka_bootstrap (str): Name of kafka bootstrap server
        retry_count (int): Number of connection retries before logging a failure

    """

    while True:

        while retry_count:
            try:
                consumer = KafkaConsumer(
                    config_name,
                    bootstrap_servers=[kafka_bootstrap],
                    key_deserializer=lambda x: x.decode('utf-8')
                )
                retry_count = 0 

            except KeyboardInterrupt:
                print("Shutting down")
                sys.exit(0)

            except:
                print("No consumers available.")
                print("Retrying...")
                retry_count -= 1

        if consumer is None:
            print("Unable to connect to Kafka bootstrap server.")
            sys.exit(0)

        elif consumer.bootstrap_connected():

            # initialize so can seek to beginning to get latest compacted state
            while not consumer._client.poll(): continue

            consumer.seek_to_beginning()

            for message in consumer:

                try:

                    if "config:/" in message.key:
                        val = json.loads(message.value.decode('utf-8'))
                        pv = message.key.split("/")[-1]

                        # if enabled, write alarm
                        print(f"writing alarm {pv}FP")
                        if val.get("enabled") is not None:
                            # will be false
                            epics.caput(f"{pv}FP", 1)

                        else:
                            epics.caput(f"{pv}FP", 0)

                    elif "state:" in message.key:
                        print(f"writing alarm {pv}ACK")
                        if val.get("severity"):
                            if "ACK" in val.get("severity"):
                                epics.caput(f"{pv}ACK", 1)

                            else:
                                epics.caput(f"{pv}ACK", 0)
                    assert 1 == 5

                except KeyboardInterrupt:
                    print("Shutting down...")
                    sys.exit(0)

                
                except Exception as e:
                    print(e)

        else:
            print("Unable to connect to Kafka bootstrap server.")
            sys.exit(0)





if __name__ == "__main__":
    import sys
    config_name = sys.argv[1]
    kafka_bootstrap = sys.argv[2]
    monitor(config_name, kafka_bootstrap)
