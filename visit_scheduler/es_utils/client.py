from elasticsearch import Elasticsearch
import os
import dotenv
from kubernetes import client, config
from kubernetes.config import ConfigException


def get_k8s_es_credits(v1):
    print("K8s...")

def get_creds():
    try:
        config.load_kube_config()
    except ConfigException:
        dotenv.load_dotenv()
        return os.getenv("ES_HOST"), os.getenv("ES_PASS"), os.getenv("ES_LOGIN")
    v1 = client.CoreV1Api()
    return get_k8s_es_credits(v1)


def get_es_client():
    host, es_pass, es_login = get_creds()
    return Elasticsearch(host, basic_auth=(es_login, es_pass), verify_certs=False)
