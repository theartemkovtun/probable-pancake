import logging
from dotenv import load_dotenv
import time
import services
import math
import logger

load_dotenv('.env')


def message_handler(ch, method, _, data):
    try:
        start_time = time.time()
        ch.basic_ack(delivery_tag=method.delivery_tag)

        media_id = data.decode().upper()
        folders_path = '/'.join(list(media_id[:4]))
        filepath = f'periphery/{folders_path}/{media_id}.mxf'

        logger.info(f"{media_id}: New item has been retrieved")

        periphery_stats = services.get_periphery_stats(filepath)
        filepath = periphery_stats.filepath

        if periphery_stats is not None:
            logging.info(f"{media_id}: Periphery data successfully fetched")
        else:
            logging.error(f"{media_id}: Failed fetched periphery data")

        azure_data = services.get_azure_data_tables_data(media_id)

        if azure_data is not None:
            logging.info(f"{media_id}: Azure data successfully fetched")
        else:
            logging.error(f"{media_id}: Failed fetched Azure data")

        xen_data = services.get_xendata(media_id)

        if xen_data is not None:
            logging.info(f"{media_id}: Xen data successfully fetched")
        else:
            logging.error(f"{media_id}: Failed fetched Xen data")

        era = services.identify_era(azure_data.created)

        logging.info(f"{media_id}: Era identified - {era}")
        logging.info(f"{media_id}: Hashing started")

        hashes = services.get_file_hashes(filepath, math.ceil(periphery_stats.size / 1000000000))

        logger.info(f"{media_id}: MD5 - {hashes.md5}, SHA3-512 - {hashes.sha3_512}")
        logger.success(f"{media_id}: Finished. Took {time.time() - start_time} seconds")

    except Exception as e:
        logging.error(repr(e))


time.sleep(15)

for _ in range(10):
    td = services.RabbitMqThreadedConsumer(message_handler)
    td.start()
