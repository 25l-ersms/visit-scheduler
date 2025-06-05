from elasticsearch import Elasticsearch
from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException

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


def get_es_client() -> Elasticsearch:
    host, es_pass, es_login = get_creds()
    settings = ElasticsearchSettings()

    if settings.CACERT_PATH:
        client = Elasticsearch(host, ca_certs=settings.CACERT_PATH, basic_auth=(es_login, es_pass), verify_certs=True)
    else:
        client = Elasticsearch(host, basic_auth=(es_login, es_pass), verify_certs=False)
    return client
