import os

from kafka import KafkaProducer


def get_kafka_config() -> dict:
    host = os.getenv("KAFKA_HOST") or ""
    return {
        "host": host,
    }


def send_message(msg: str) -> None:
    """
    Send a message to the Kafka topic.
    """
    # Example message
    kafka_config = get_kafka_config()
    producer = KafkaProducer(
        bootstrap_servers=[rf"{kafka_config['host']}\:9092"]
    )  # TODO consider moving to singleton or sth
    print("Sending message to Kafka topic")
    producer.send("test_topic", value=msg.encode("utf-8"))
