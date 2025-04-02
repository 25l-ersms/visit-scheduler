from elastic_transport import ObjectApiResponse

from visit_scheduler.es_utils.client import get_es_client


def get_all() -> ObjectApiResponse:
    es_client = get_es_client()
    return es_client.search(index="test_index", body={"query": {"match_all": {}}})
