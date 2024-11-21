from models import PeripheryStats, AzureData, Xendata, RecordEra
import logger
from datetime import datetime, timedelta


def validate_media(media_id: str, era: RecordEra, periphery_data: PeripheryStats, azure_data: AzureData,
                   xendata: Xendata,
                   md5_hash: str, logs: list[str]):
    totalFailed = 0

    logger.info(media_id, "Rules validation started", logs)

    totalFailed += validate_shared_rules(media_id, periphery_data, azure_data, xendata, md5_hash, logs)

    if era == RecordEra.Pre2017:
        totalFailed += validate_pre2017_era(media_id, periphery_data, azure_data, xendata, logs)
    elif era == RecordEra.Migration2017Era:
        totalFailed += validate_migration_2017_era(media_id, periphery_data, azure_data, xendata, logs)
    elif era == RecordEra.Between2017And2022:
        totalFailed += validate_between_2017_and_2022_era(media_id, periphery_data, azure_data, xendata, logs)
    else:
        totalFailed += validate_post_2022_era(media_id, periphery_data, azure_data, xendata, logs)

    logger.info(media_id, "Rules validation finished", logs)

    return totalFailed


def validate_shared_rules(media_id: str, periphery_data: PeripheryStats, azure_data: AzureData, xendata: Xendata,
                          md5_hash: str, logs: list[str]):
    totalFailed = 0

    totalFailed += validate_and_log(media_id,
                                    azure_data.width in [720, 1920] and azure_data.height in [608, 480, 1080],
                                    "Resolution appropriate", logs)
    totalFailed += validate_and_log(media_id,
                                    azure_data.frame_rate in [25, 29.97],
                                    "Framerate appropriate", logs)

    totalFailed += validate_and_log(media_id,
                                    azure_data.md5_hash == md5_hash,
                                    "Azure MD5 = calculated periphery file MD5", logs)

    totalFailed += validate_and_log(media_id,
                                    periphery_data.size == xendata.size,
                                    "P size == X size", logs)

    totalFailed += validate_and_log(media_id,
                                    periphery_data.creation_date <= xendata.creation_date,
                                    "P created <= X created", logs)

    totalFailed += validate_and_log(media_id,
                                    azure_data.created <= xendata.creation_date,
                                    "A created <= X created", logs)

    totalFailed += validate_and_log(media_id,
                                    periphery_data.modified_date >= periphery_data.creation_date,
                                    "P modified >= P created", logs)

    return totalFailed


def validate_pre2017_era(media_id: str, periphery_data: PeripheryStats, azure_data: AzureData, xendata: Xendata, logs: list[str]):
    totalFailed = 0
    thirty_days_prior_to_x_modified = xendata.modification_date - timedelta(days=30)

    logger.info(media_id, "Pre2017 era rules validation started", logs)

    totalFailed += validate_and_log(media_id,
                                    datetime(2017, 8, 24) <= periphery_data.creation_date <= datetime(2017, 11, 29),
                                    "P Created between 24 Aug 2017 and 29 Nov 2017", logs)

    totalFailed += validate_and_log(media_id,
                                    datetime(2017, 8, 24) <= periphery_data.modified_date <= datetime(2017, 11, 29),
                                    "P Modified between 24 Aug 2017 and 29 Nov 2017", logs)

    totalFailed += validate_and_log(media_id,
                                    azure_data.created <= datetime(2017, 8, 24),
                                    "A Created <= 24 Aug 2017", logs)

    totalFailed += validate_and_log(media_id,
                                    azure_data.timestamp.date() == datetime(2022, 6, 17).date(),
                                    "A Record time (timestamp) is 2022-06-17", logs)

    totalFailed += validate_and_log(media_id,
                                    thirty_days_prior_to_x_modified <= xendata.creation_date <= xendata.modification_date,
                                    "X Created <= 30 days of X Modified", logs)

    return totalFailed


def validate_migration_2017_era(media_id: str, periphery_data: PeripheryStats, azure_data: AzureData, xendata: Xendata, logs: list[str]):
    totalFailed = 0

    twenty_one_day_prior_to_p_created = periphery_data.creation_date - timedelta(days=21)
    one_day_prior_to_p_created = periphery_data.creation_date - timedelta(days=1)
    one_day_prior_to_x_created = xendata.creation_date - timedelta(days=1)

    totalFailed += validate_and_log(media_id,
                                    datetime(2017, 8, 24) <= periphery_data.creation_date <= datetime(2022, 6, 17),
                                    "P Created between 24 Aug 2017 and 17 June 2022", logs)

    totalFailed += validate_and_log(media_id,
                                    azure_data.created >= datetime(2017, 8, 24),
                                    "A Created >= 24 Aug 2017", logs)

    totalFailed += validate_and_log(media_id,
                                    azure_data.timestamp.date() == datetime(2022, 6, 17).date(),
                                    "A Record time (A Timestamp) is 2022-6-17", logs)

    totalFailed += validate_and_log(media_id,
                                    azure_data.created >= twenty_one_day_prior_to_p_created,
                                    "A Created is 21d to P Created", logs)

    totalFailed += validate_and_log(media_id,
                                    azure_data.timestamp >= one_day_prior_to_p_created,
                                    "A Record time (A Timestamp) is 1d to P Created", logs)

    totalFailed += validate_and_log(media_id,
                                    xendata.modification_date >= one_day_prior_to_x_created,
                                    "X Modified is within 1d of X Created", logs)

    return totalFailed


def validate_between_2017_and_2022_era(media_id: str, periphery_data: PeripheryStats, azure_data: AzureData, xendata: Xendata, logs: list[str]):
    totalFailed = 0

    one_day_prior_to_p_created = periphery_data.creation_date - timedelta(days=1)
    one_day_prior_to_x_created = xendata.creation_date - timedelta(days=1)

    totalFailed += validate_and_log(media_id,
                                    datetime(2017, 8, 24) <= periphery_data.creation_date <= datetime(2022, 6, 17),
                                    "P Created between 24 Aug 2017 and 17 June 2022", logs)

    totalFailed += validate_and_log(media_id,
                                    azure_data.created >= datetime(2017, 8, 24),
                                    "A Created >= 24 Aug 2017", logs)

    totalFailed += validate_and_log(media_id,
                                    azure_data.timestamp.date() == datetime(2022, 6, 17).date(),
                                    "A Record time (A Timestamp) is 2022-6-17", logs)

    totalFailed += validate_and_log(media_id,
                                    azure_data.created >= one_day_prior_to_p_created,
                                    "A Created is 1d to P Created", logs)

    totalFailed += validate_and_log(media_id,
                                    azure_data.timestamp >= one_day_prior_to_p_created,
                                    "A Record time (A Timestamp) is 1d to P Created", logs)

    totalFailed += validate_and_log(media_id,
                                    xendata.modification_date >= one_day_prior_to_x_created,
                                    "X Modified is within 1d of X Created", logs)

    return totalFailed


def validate_post_2022_era(media_id: str, periphery_data: PeripheryStats, azure_data: AzureData, xendata: Xendata, logs: list[str]):
    totalFailed = 0

    one_day_prior_to_p_created = periphery_data.creation_date - timedelta(days=1)
    one_day_prior_to_a_created = azure_data.created - timedelta(days=1)

    totalFailed += validate_and_log(media_id,
                                    periphery_data.creation_date >= datetime(2017, 8, 24),
                                    "P Created >= 24 Aug 2017", logs)

    totalFailed += validate_and_log(media_id,
                                    azure_data.created >= datetime(2022, 6, 17),
                                    "A Created >= 17 June 2022", logs)

    totalFailed += validate_and_log(media_id,
                                    azure_data.timestamp >= datetime(2022, 6, 17),
                                    "A Record time (A Timestamp) >= 17 June 2022", logs)

    totalFailed += validate_and_log(media_id,
                                    azure_data.created >= one_day_prior_to_p_created,
                                    "A Created is 1d to P Created", logs)

    totalFailed += validate_and_log(media_id,
                                    azure_data.timestamp >= one_day_prior_to_a_created,
                                    "A Record time (A Timestamp) is within 1 day of A created", logs)

    totalFailed += validate_and_log(media_id,
                                    xendata.modification_date >= xendata.creation_date,
                                    "X Modified >= X Created", logs)

    return totalFailed


def validate_and_log(media_id: str, rule: bool, message: str, logs: list[str]):
    if rule:
        logger.info(media_id, f"{message} - true", logs)
    else:
        logger.warning(media_id, f"{message} - false", logs)

    return int(not rule)
