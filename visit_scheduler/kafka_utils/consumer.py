import json

import confluent_kafka  # type: ignore[import-untyped]

from visit_scheduler.es_utils.handler import add_rating, add_vendor
from visit_scheduler.es_utils.models import RatingModel, VendorModel
from visit_scheduler.kafka_utils.common import KafkaTokenProvider, KafkaTopics
from visit_scheduler.package_utils.logger_conf import logger
from visit_scheduler.package_utils.settings import KafkaSettings, kafka_authentication_scheme_t


def _get_kafka_consumer_config(
    bootstrap_url: str, group_id: str, auth_scheme: kafka_authentication_scheme_t
) -> dict[str, (str | int | bool | object | None)]:
    config = {
        "bootstrap.servers": bootstrap_url,
        "group.id": group_id,
        "enable.auto.commit": True,
        "auto.offset.reset": "earliest",
    }

    if auth_scheme == "oauth":
        logger.debug("Using OAuth for Kafka authentication")
        token_provider = KafkaTokenProvider()

        config = config | {
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "OAUTHBEARER",
            "oauth_cb": token_provider.get_token,
        }
    else:
        logger.debug("Assuming Kafka authentication is not required")

    return config


def _handle_vendor_message(message: str) -> None:
    logger.info(f"Processing vendor message: {message}")
    data = json.loads(message)

    # Transform incoming data to match our model
    vendor_data = VendorModel(
        name=data["vendor_name"],
        location=[data["address"]["latitude"], data["address"]["longitude"]],
        user_id=data["vendor_id"],
        service_types=[service_type["name"] for service_type in data["service_types"]],
        vendor_email=data["user"]["email"],
    )
    add_vendor(vendor_data)


def _handle_rating_message(message: str) -> None:
    logger.info(f"Processing rating message: {message}")
    rating_data = RatingModel(**json.loads(message))
    add_rating(rating_data)


def listen_to_kafka() -> None:
    settings = KafkaSettings()

    auth_scheme: kafka_authentication_scheme_t = settings.AUTHENTICATION_SCHEME

    config = _get_kafka_consumer_config(
        bootstrap_url=settings.BOOTSTRAP_URL, group_id=settings.GROUP_ID, auth_scheme=auth_scheme
    )
    topic_handlers = {
        KafkaTopics.USERS.topic_name: _handle_vendor_message,
        KafkaTopics.RATINGS.topic_name: _handle_rating_message,
    }

    consumer = confluent_kafka.Consumer(config)
    consumer.subscribe([x.topic_name for x in KafkaTopics])
    logger.info(f"Listening for messages on Kafka topics '{', '.join([x.topic_name for x in KafkaTopics])}'...")

    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            logger.error(f"Kafka error: {msg.error()}")
            continue
        topic = msg.topic()
        message = msg.value().decode("utf-8")

        handler = topic_handlers.get(topic)
        handler(message)


def enable_listen_to_kafka() -> None:
    """
    Enable the Kafka consumer to listen for messages.
    """
    logger.info("Starting Kafka consumer...")
    listen_to_kafka()
