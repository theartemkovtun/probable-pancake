import os
from models import PeripheryStats, FileHashes, AzureData, RecordEra, Xendata
from azure.core.credentials import AzureSasCredential
from datetime import datetime
from azure.data.tables import TableServiceClient
import hashlib
import threading
import pika
import base64
import pymssql
import logging

class RabbitMqThreadedConsumer(threading.Thread):

    def __init__(self, callback):
        threading.Thread.__init__(self)
        credentials = pika.PlainCredentials(
            username=os.environ.get("RABBITMQ_USERNAME"),
            password=os.environ.get("RABBITMQ_PASSWORD")
        )
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            os.environ.get("RABBITMQ_HOST"), os.environ.get("RABBITMQ_PORT"), '/', credentials)
        )

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=os.environ.get("RABBITMQ_QUEUE_NAME"))
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(os.environ.get("RABBITMQ_QUEUE_NAME"), callback)

    def run(self):
        self.channel.start_consuming()


def read_in_chunks(file_object, chunk_size=300000000):
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
            raise Exception("File does not found in the periphery storage")

    return PeripheryStats(correct_path, int(stats.st_size), datetime.fromtimestamp(int(stats.st_ctime)),
                          datetime.fromtimestamp(int(stats.st_mtime)), datetime.fromtimestamp(int(stats.st_atime)))


def get_azure_data_tables_data(media_id: str):
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
                         data["Duration"], int(data["FileLength"]), data["FileName"],
                         int(data["FrameRate"]), int(data["Height"]), int(data["Width"]),
                         base64.b64decode(data["MD5"]).decode())


def get_xendata(media_id: str):

    # b8ffd07f-4127-41cd-8dbf-3675a897225d -> 0/ITN/b/8/f/f/b8ffd07f-4127-41cd-8dbf-3675a897225d.mxf
    key = '0/ITN/' + '/'.join(list(media_id[:4])) + '/' + media_id + '.mxf'

    conn = pymssql.connect(os.environ.get("XENDATA_SERVER"), os.environ.get("XENDATA_USER"),
                           os.environ.get("XENDATA_PASSWORD"), os.environ.get("XENDATA_DATABASE"))
    cursor = conn.cursor(as_dict=True)

    cursor.execute(f"""SELECT * FROM OPENQUERY([XENDATA], 'SELECT CreationTime, ModificationTime, Size FROM FILES WHERE Path LIKE "${key}"')""")
    row = cursor.fetchone()

    conn.close()

    return Xendata(
        creation_date=datetime.strptime(row[0][:20], "%Y-%m-%dT%H:%M:%S"),
        modification_date=datetime.strptime(row[1][:20], "%Y-%m-%dT%H:%M:%S"),
        size=int(row[2])
    )


def get_file_hashes(filepath: str):
    md5 = hashlib.md5()
    sha3512 = hashlib.sha3_512()

    with open(filepath, 'rb') as file:
        for piece in read_in_chunks(file):
            md5.update(piece)
            sha3512.update(piece)

    return FileHashes(md5.hexdigest(), sha3512.hexdigest())


def identify_era(date: datetime):
    if date < datetime(2017, 8, 24):
        return RecordEra.Pre2017
    elif date < datetime(2017, 11, 29):
        return RecordEra.Migration2017Era
    elif date < datetime(2022, 6, 17):
        return RecordEra.Between2017And2022
    else:
        return RecordEra.Post2022
