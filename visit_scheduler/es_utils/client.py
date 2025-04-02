from elasticsearch import Elasticsearch
import os
import dotenv
from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException


def get_k8s_es_credits(v1: client.CoreV1Api) -> tuple[str, str, str]:
    print("K8s...")
    return "", "", ""

def get_creds() -> tuple[str, str, str]:
    try:
        config.load_kube_config() # type: ignore[attr-defined]
    except ConfigException:
        dotenv.load_dotenv()
        return os.getenv("ES_HOST") or "", os.getenv("ES_PASS") or "", os.getenv("ES_LOGIN") or ""
    v1 = client.CoreV1Api()
    return get_k8s_es_credits(v1)


def get_es_client() -> Elasticsearch:
    host, es_pass, es_login = get_creds()
    return Elasticsearch(host, basic_auth=(es_login, es_pass), verify_certs=False)
