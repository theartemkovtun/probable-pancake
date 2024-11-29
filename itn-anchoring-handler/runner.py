from dotenv import load_dotenv
from models import RecordEra
import time
import services
import math
import logger
import validators
import pika
import os

load_dotenv('.env')


def message_handler(ch, method, _, data):
    log = []
    media_id = data.decode().upper()
    validation_errors = 0
    is_anchor_success = False
    era = RecordEra.Rest

    try:
        start_time = time.time()
        ch.basic_ack(delivery_tag=method.delivery_tag)

        folders_path = '/'.join(list(media_id[:4]))
        filepath = f'periphery/{folders_path}/{media_id}.mxf'

        logger.info(media_id, "New item has been retrieved", log)

        periphery_stats = services.get_periphery_stats(filepath)
        logger.info(media_id, "Periphery data successfully fetched", log)
        filepath = periphery_stats.filepath

        azure_data = services.get_azure_data_tables_data(media_id)
        logger.info(media_id, "Azure data successfully fetched", log)

        xen_data = services.get_xendata(media_id)
        logger.info(media_id, "Xen data successfully fetched", log)

        era = services.identify_era(azure_data.created)

        logger.info(media_id, f"Era identified - {era.name}", log)
        logger.info(media_id, "Hashing started", log)

        hashes = services.get_file_hashes(filepath, math.ceil(periphery_stats.size / 1000000000))

        logger.info(media_id, "Hashing finished successfully", log)
        logger.info(media_id, f"SHA3-512: {hashes.sha3_512}", log)

        validation_errors = validators.validate_media(media_id, era, periphery_stats,
                                                      azure_data, xen_data, hashes.md5, log)

        metadata = {
            "era": era.name,
            "periphery": dict(periphery_stats),
            "azure": dict(azure_data),
            "xendata": dict(xen_data)
        }

        services.submit_anchor_request(media_id, filepath.split('/')[-1], hashes.sha3_512, metadata)
        is_anchor_success = True

        logger.success(media_id, f"Finished. Took {time.time() - start_time} seconds", log)

    except Exception as e:
        logger.error(media_id, f"{repr(e)}", log)

    services.save_log_file(media_id, "\n".join(log), era, is_anchor_success, validation_errors)


time.sleep(15)

credentials = pika.PlainCredentials(
    username=os.environ.get("RABBITMQ_USERNAME"),
    password=os.environ.get("RABBITMQ_PASSWORD")
)
connection = pika.BlockingConnection(pika.ConnectionParameters(
    os.environ.get("RABBITMQ_HOST"), os.environ.get("RABBITMQ_PORT"), '/', credentials, heartbeat=0)
)

channel = connection.channel()
channel.queue_declare(queue=os.environ.get("RABBITMQ_QUEUE_NAME"))
channel.basic_qos(prefetch_count=1)
channel.basic_consume(os.environ.get("RABBITMQ_QUEUE_NAME"), message_handler)
channel.start_consuming()