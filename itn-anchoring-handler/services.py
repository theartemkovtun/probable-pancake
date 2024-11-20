import json
import os
import time
import requests
from models import PeripheryStats, FileHashes, AzureData, RecordEra, Xendata
from azure.core.credentials import AzureSasCredential
from datetime import datetime
from azure.data.tables import TableServiceClient
import hashlib
import threading
import pika
import base64
import pymssql


class RabbitMqThreadedConsumer(threading.Thread):

    def __init__(self, callback):
        threading.Thread.__init__(self)
        credentials = pika.PlainCredentials(
            username=os.environ.get("RABBITMQ_USERNAME"),
            password=os.environ.get("RABBITMQ_PASSWORD")
        )
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            os.environ.get("RABBITMQ_HOST"), os.environ.get("RABBITMQ_PORT"), '/', credentials, heartbeat=0)
        )

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=os.environ.get("RABBITMQ_QUEUE_NAME"))
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(os.environ.get("RABBITMQ_QUEUE_NAME"), callback)

    def run(self):
        self.channel.start_consuming()


def read_in_chunks(file_object, chunk_size=1000000000):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def get_periphery_stats(filepath: str):
    try:
        stats = os.stat(filepath)
        correct_path = filepath
    except:
        # check for same file but with extension capitalized
        correct_path = filepath.replace('mxf', 'MXF')
        try:
            stats = os.stat(correct_path)
        except:
            raise Exception(f"Failed to fetch periphery data")

    return PeripheryStats(correct_path, int(stats.st_size), datetime.fromtimestamp(int(stats.st_ctime)),
                          datetime.fromtimestamp(int(stats.st_mtime)), datetime.fromtimestamp(int(stats.st_atime)))


def get_azure_data_tables_data(media_id: str):
    try:
        partition_key = f"ITN_{media_id[:3]}"
        row_key = ''.join(media_id[3:].split('-'))

        with TableServiceClient(
                endpoint=os.environ.get("AZURE_DATA_TABLE_CONNECTION_STRING"),
                credential=AzureSasCredential(os.environ.get("AZURE_DATA_TABLE_SAS"))
        ) as table_service_client:
            table_client = table_service_client.get_table_client(
                table_name=os.environ.get("AZURE_DATA_TABLE_NAME"))

            data = table_client.get_entity(partition_key, row_key)
            timestamp = str(data._metadata["timestamp"])[:19]

            return AzureData(datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"), data["AspectRatio"],
                             datetime.strptime(str(data["Created"])[:19], "%Y-%m-%d %H:%M:%S"), data["Codec"],
                             data["Duration"], int(data["FileLength"].value), data["FileName"],
                             int(data["FrameRate"]), int(data["Height"]), int(data["Width"]),
                             base64.b64encode(data["MD5"]).decode())
    except:
        raise Exception(f"Failed to fetch Azure data")


def get_xendata(media_id: str):

    try:

        # b8ffd07f-4127-41cd-8dbf-3675a897225d -> 0/ITN/b/8/f/f/b8ffd07f-4127-41cd-8dbf-3675a897225d.mxf
        key = '0/ITN/' + '/'.join(list(media_id[:4])) + '/' + media_id + '.mxf'

        conn = pymssql.connect(os.environ.get("XENDATA_SERVER"), os.environ.get("XENDATA_USER"),
                               os.environ.get("XENDATA_PASSWORD"), os.environ.get("XENDATA_DATABASE"))
        cursor = conn.cursor(as_dict=True)

        query = f"""SELECT * FROM OPENQUERY([XENDATA], 'SELECT CreationTime, ModificationTime, Size FROM FILES WHERE Path LIKE "{key}"')"""

        cursor.execute(query)
        row = cursor.fetchone()

        conn.close()

        return Xendata(
            creation_date=row['CreationTime'],
            modification_date=row['ModificationTime'],
            size=row['Size']
        )
    except:
        raise Exception("Failed to fetch Xen data")


def get_file_hashes(filepath: str, total_chunks: int):
    smart_time = time.time()
    current_chunk = 1

    md5 = hashlib.md5()
    sha3512 = hashlib.sha3_512()

    with open(filepath, 'rb') as file:
        for piece in read_in_chunks(file):
            read_time = time.time() - smart_time
            smart_time = time.time()

            md5.update(piece)
            sha3512.update(piece)

            hash_time = time.time() - smart_time
            smart_time = time.time()

            print(f"{filepath[-40:-4]}: Chunk ({current_chunk}/{total_chunks}): read time - {read_time} sec, hash time - {hash_time} sec")

            current_chunk += 1

    return FileHashes(base64.b64encode(md5.digest()).decode(), sha3512.hexdigest())


def identify_era(date: datetime):
    if date < datetime(2017, 8, 24):
        return RecordEra.Pre2017
    elif date < datetime(2017, 11, 29):
        return RecordEra.Migration2017Era
    elif date < datetime(2022, 6, 17):
        return RecordEra.Between2017And2022
    else:
        return RecordEra.Post2022


def submit_anchor_request(media_id: str, sha3_512_hash: str, metadata):

    request_body = {
        "hash": sha3_512_hash,
        "name": media_id,
        "metadata": json.dumps(metadata, default=str)
    }

    headers = {"OO-ANCHORING-KEY": os.environ.get("ANCHORING_KEY")}

    response = requests.post(f"{os.environ.get('ANCHORING_URL')}/api/anchor", headers=headers, json=request_body)

    if response.status_code != 200:
        raise Exception(F"Failed to submit anchor request: {response.status_code}, {response.text}")