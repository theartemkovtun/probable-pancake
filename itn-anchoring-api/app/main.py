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


@app.post("/queue-for-anchoring/{media_id}")
async def queue_single(media_id: str):
    rabbit_client = RabbitClient()
    if not is_valid_uuid(media_id):
        raise HTTPException(status_code=404, detail="'id' has to be UUIDv4 format")

    rabbit_client.publish(media_id)


@app.post("/queue-for-anchoring")
async def queue_single(items: list[AnchorItem]):
    rabbit_client = RabbitClient()

    ids = []
    for item in items:
        if not is_valid_uuid(item.id):
            raise HTTPException(status_code=404, detail="'id' has to be UUIDv4 format")
        ids.append(item.id)

    rabbit_client.publish(ids)

@app.get("/queue/messages-number")
async def queue_single():
    rabbit_client = RabbitClient()

    return {
        "messages": rabbit_client.get_number_of_messages()
    }