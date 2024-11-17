from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
from rabbit_client import RabbitClient
from uuid import UUID

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