from visit_scheduler.app.models.models import InsertModel
from visit_scheduler.es_utils.client import get_es_client

def add_element(data: InsertModel) -> None:
    print(data) # TODO add real logger
    client = get_es_client()
    client.indices.create(index='test_index')
    client.index(index='test_index', id="1", body={'test': 'test'})