import logging
from dotenv import load_dotenv
import time
import services

logger = logging.getLogger(__name__)
load_dotenv('.env')


def message_handler(ch, method, _, data):
    try:
        start_time = time.time()
        ch.basic_ack(delivery_tag=method.delivery_tag)

        media_id = data.decode().upper()
        folders_path = '/'.join(list(media_id[:4]))
        filepath = f'periphery/{folders_path}/{media_id}.mxf'

        print(f"New item: {media_id}")

        periphery_stats = services.get_periphery_stats(filepath)
        filepath = periphery_stats.filepath

        azure_data = services.get_azure_data_tables_data(media_id)

        xen_data = services.get_xendata(media_id)

        era = services.identify_era(azure_data.created)

        hashes = services.get_file_hashes(filepath)

        logging.warning(dict(hashes))

        logging.warning(f"{media_id}: Took {time.time() - start_time} seconds")

    except Exception as e:
        logging.error(repr(e))


time.sleep(15)

for _ in range(10):
    td = services.RabbitMqThreadedConsumer(message_handler)
    td.start()
