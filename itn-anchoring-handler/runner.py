import logging
from dotenv import load_dotenv
import time
import services

logger = logging.getLogger(__name__)
load_dotenv('.env')


def message_handler(ch, method, _, data):
    try:
        media_id = data.decode().lower()
        folders_path = '/'.join(list(media_id[:4]))
        filepath = f'periphery/{folders_path}/{media_id}.mxf'

        periphery_stats = services.get_periphery_stats(filepath)
        filepath = periphery_stats.filepath

        logging.warning(dict(periphery_stats))

        azure_data = services.get_azure_data_tables_data(media_id)

        logging.warning(dict(azure_data))

        xen_data = services.get_xendata(media_id)

        logging.warning(dict(xen_data))

        era = services.identify_era(azure_data.created)

        logging.warning(dict(era))

        hashes = services.get_file_hashes(filepath)

        logging.warning(dict(hashes))

    except Exception as e:
        logging.error(repr(e))

    ch.basic_ack(delivery_tag=method.delivery_tag)


time.sleep(15)

for _ in range(3):
    td = services.RabbitMqThreadedConsumer(message_handler)
    td.start()
