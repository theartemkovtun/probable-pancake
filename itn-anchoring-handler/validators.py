from models import PeripheryStats, AzureData, Xendata, RecordEra
import logger


def validate_media(era: RecordEra, periphery_data: PeripheryStats, azure_data: AzureData, xendata: Xendata,
                   md5_hash: str, logs: list[str]):
    return validate_shared_rules(periphery_data, azure_data, xendata, md5_hash, logs)


def validate_shared_rules(periphery_data: PeripheryStats, azure_data: AzureData, xendata: Xendata,
                          md5_hash: str, logs: list[str]):
    totalFailed = 0

    logger.info("Rules validation started", logs)

    totalFailed += validate_and_log(
        azure_data.width in [720, 1920] and azure_data.height in [608, 480, 1080], "Resolution appropriate", logs)
    totalFailed += validate_and_log(
        azure_data.frame_rate in [25, 29.97], "Framerate appropriate", logs)

    totalFailed += validate_and_log(
        azure_data.md5_hash == md5_hash, "Azure MD5 = calculated periphery file MD5", logs)

    totalFailed += validate_and_log(
        periphery_data.size == xendata.size, "P size == X size", logs)

    totalFailed += validate_and_log(
        periphery_data.creation_date <= xendata.creation_date, "P created <= X created", logs)

    totalFailed += validate_and_log(
        azure_data.created <= xendata.creation_date, "A created <= X created", logs)

    totalFailed += validate_and_log(
        periphery_data.modified_date >= periphery_data.creation_date, "P modified >= P created", logs)

    logger.info("Rules validation finished", logs)

    return totalFailed


def validate_and_log(rule: bool, message: str, logs: list[str]):
    if rule:
        logger.info(f"{message} - true", logs)
    else:
        logger.warning(f"{message} - false", logs)

    return int(rule)