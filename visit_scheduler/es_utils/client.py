import functools

from elasticsearch import Elasticsearch
from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException

from visit_scheduler.es_utils.defenitions import es_mapping_time_slot, es_mapping_vendor
from visit_scheduler.es_utils.models import ES_INDEX_TIME_SLOTS, ES_INDEX_VENDORS
from visit_scheduler.package_utils.logger_conf import logger
from visit_scheduler.package_utils.settings import ElasticsearchSettings


def get_k8s_es_credits(v1: client.CoreV1Api) -> tuple[str, str, str]:
    print("K8s...")
    return "", "", ""


def get_creds() -> tuple[str, str, str]:
    try:
        config.load_kube_config()  # type: ignore[attr-defined]
    except ConfigException:
        settings = ElasticsearchSettings()

        return settings.HOST, settings.PASS, settings.LOGIN
    v1 = client.CoreV1Api()
    return get_k8s_es_credits(v1)


def init_es(es_client: Elasticsearch) -> None:
    if not es_client.indices.exists(index=ES_INDEX_VENDORS):
        es_client.indices.create(index=ES_INDEX_VENDORS, body={"mappings": es_mapping_vendor})
        logger.info(f"Created index {ES_INDEX_VENDORS}")
    if not es_client.indices.exists(index=ES_INDEX_TIME_SLOTS):
        es_client.indices.create(index=ES_INDEX_TIME_SLOTS, body={"mappings": es_mapping_time_slot})
        logger.info(f"Created index {ES_INDEX_TIME_SLOTS}")
    logger.info("Elasticsearch initialized")


def _create_es_client() -> Elasticsearch:
    host, es_pass, es_login = get_creds()
    settings = ElasticsearchSettings()

    if settings.CACERT_PATH:
        client = Elasticsearch(host, ca_certs=settings.CACERT_PATH, basic_auth=(es_login, es_pass), verify_certs=True)
    else:
        client = Elasticsearch(host, basic_auth=(es_login, es_pass), verify_certs=False)
    init_es(client)
    return client


@functools.lru_cache(maxsize=1)
def get_es_client() -> Elasticsearch:
    """Get a cached Elasticsearch client instance.
    The client is created only once and cached for subsequent calls."""
    logger.info("Initializing Elasticsearch client")
    client = _create_es_client()
    logger.info("Initialized Elasticsearch client")
    return client
