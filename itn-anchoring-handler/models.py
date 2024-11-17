from enum import Enum
from datetime import datetime


class RecordEra(Enum):
    Pre2017 = 1
    Migration2017Era = 2
    Between2017And2022 = 3
    Post2022 = 4


class PeripheryStats:

    def __init__(self, filepath: str, size: int, creation_date: datetime, modified_date: datetime,
                 last_access_date: datetime):
        self.filepath: str = filepath
        self.size: int = size
        self.creation_date: datetime = creation_date
        self.modified_date: datetime = modified_date
        self.last_access_date: datetime = last_access_date

    def __iter__(self):
        return iter([
            ('filepath', self.filepath),
            ('size', self.size),
            ('creationDate', self.creation_date),
            ('modifiedDate', self.modified_date),
            ('lastAccessDate', self.last_access_date),
        ])


class FileHashes:

    def __init__(self, md5: str, sha3_512: str):
        self.md5: str = md5
        self.sha3_512: str = sha3_512

    def __iter__(self):
        return iter([('md5', self.md5), ('sha3512', self.sha3_512)])


class AzureData:

    def __init__(self,
                 timestamp: datetime,
                 aspect_ratio: str,
                 created: datetime,
                 codec: str,
                 duration: str,
                 file_length: int,
                 file_name: str,
                 frame_rate: int,
                 height: int,
                 width: int,
                 md5_hash: str):
        self.timestamp: datetime = timestamp
        self.aspect_ratio: str = aspect_ratio
        self.created: datetime = created
        self.codec: str = codec
        self.duration: str = duration
        self.file_length: int = file_length
        self.file_name: str = file_name
        self.frame_rate: int = frame_rate
        self.height: int = height
        self.width: int = width
        self.md5_hash: str = md5_hash

    def __iter__(self):
        return iter([
            ('timestamp', self.timestamp),
            ('aspectRatio', self.aspect_ratio),
            ('created', self.created),
            ('codec', self.codec),
            ('duration', self.duration),
            ('fileLength', self.file_length),
            ('fileName', self.file_name),
            ('frameRate', self.frame_rate),
            ('height', self.height),
            ('width', self.width),
            ('md5Hash', self.md5_hash),
        ])


class Xendata:

    def __init__(self, creation_date: datetime, modification_date: datetime, size: int):
        self.creation_date: datetime = creation_date
        self.modification_date: datetime = modification_date
        self.size: int = size

    def __iter__(self):
        return iter([
            ('creationDate', self.creation_date),
            ('modificationDate', self.modification_date),
            ('size', self.size),
        ])