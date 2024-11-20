import logging
from dotenv import load_dotenv
import time
import services
import math
import logger

load_dotenv('.env')


def message_handler(ch, method, _, data):
    media_id = data.decode().upper()

    try:
        start_time = time.time()
        ch.basic_ack(delivery_tag=method.delivery_tag)

        folders_path = '/'.join(list(media_id[:4]))
        filepath = f'periphery/{folders_path}/{media_id}.mxf'

        logger.info(f"{media_id}: New item has been retrieved")

        periphery_stats = services.get_periphery_stats(filepath)
        logger.info(f"{media_id}: Periphery data successfully fetched")
        filepath = periphery_stats.filepath

        azure_data = services.get_azure_data_tables_data(media_id)
        logger.info(f"{media_id}: Azure data successfully fetched")

        xen_data = services.get_xendata(media_id)
        logger.info(f"{media_id}: Xen data successfully fetched")

        era = services.identify_era(azure_data.created)

        logger.info(f"{media_id}: Era identified - {era}")
        logger.info(f"{media_id}: Hashing started")

        hashes = services.get_file_hashes(filepath, math.ceil(periphery_stats.size / 1000000000))

        logger.info(f"{media_id}: Hashing finished successfully")

        metadata = {
            "periphery": dict(periphery_stats),
            "azure": dict(azure_data),
            "xendata": dict(xen_data)
        }

        services.submit_anchor_request(media_id, hashes.sha3_512, metadata)

        logger.success(f"{media_id}: Finished. Took {time.time() - start_time} seconds")

    except Exception as e:
        logger.error(f"{media_id}: {repr(e)}")


time.sleep(15)

for _ in range(10):
    td = services.RabbitMqThreadedConsumer(message_handler)
    td.start()
