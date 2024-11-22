from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
from rabbit_client import RabbitClient
from uuid import UUID
import services

load_dotenv()

app = FastAPI()


def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test

class AnchorItem(BaseModel):
    id: str


@app.get("/health-check")
async def health_check():
    return {"status": 'ok'}


@app.post("/queue-anchoring-single")
async def queue_single(item: AnchorItem):
    rabbit_client = RabbitClient()
    if not is_valid_uuid(item.id):
        raise HTTPException(status_code=404, detail="'id' has to be UUIDv4 format")

    rabbit_client.publish(item.id)


@app.post("/queue-anchoring")
async def queue_single(items: list[AnchorItem]):
    rabbit_client = RabbitClient()

    ids = []
    for item in items:
        if not is_valid_uuid(item.id):
            raise HTTPException(status_code=404, detail="'id' has to be UUIDv4 format")
        ids.append(item.id)

    rabbit_client.publish(ids)


@app.post("/update_metadata/{media_id}")
async def queue_single(media_id: str):
    media_id = media_id.upper()

    folders_path = '/'.join(list(media_id[:4]))
    filepath = f'periphery/{folders_path}/{media_id}.mxf'

    periphery_stats = services.get_periphery_stats(filepath)
    print(media_id, "Periphery data successfully fetched")
    filepath = periphery_stats.filepath

    azure_data = services.get_azure_data_tables_data(media_id)
    print(media_id, "Azure data successfully fetched")

    xen_data = services.get_xendata(media_id)
    print(media_id, "Xen data successfully fetched")

    era = services.identify_era(azure_data.created)
    print(media_id, f"Era identified - {era.name}")

    metadata = {
        "periphery": dict(periphery_stats),
        "azure": dict(azure_data),
        "xendata": dict(xen_data),
        "era": era.name
    }

    services.submit_metadata(media_id.lower(), metadata)

    return {"status": 'ok'}