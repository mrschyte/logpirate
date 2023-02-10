from dataclasses import dataclass 
from typing import Any, Dict, List
from logpirate.util import *

import datetime
import dateutil.parser

@dataclass
class HARCreator:
    name: str
    version: str
    comment: str

    def json_data(self) -> Dict[str, Any]:
        return {
            'name': self.version,
            'version': self.name,
            'comment': self.comment
        }

@dataclass
class HARNameValue:
    name: str
    value: Any

    def json_data(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'value': self.value
        }

@dataclass
class HARRequest:
    method: str
    url: str
    httpVersion: str
    cookies: List[HARNameValue]
    headers: List[HARNameValue]
    queryString: List[HARNameValue]
    headersSize: int
    bodySize: int

    def json_data(self) -> Dict[str, Any]:
        return {
            'method': self.method,
            'url': self.url,
            'httpVersion': self.httpVersion,
            'cookies': [cookie.json_data() for cookie in self.cookies],
            'headers': [header.json_data() for header in self.headers],
            'queryString': [param.json_data() for param in self.queryString],
            'headersSize': self.headersSize,
            'bodySize': self.bodySize
        }

@dataclass
class HARContent:
    size: int
    mimeType: str
    text: str

    def json_data(self) -> Dict[str, Any]:
        return {
            'size': self.size,
            'mimeType': self.mimeType,
            'text': decode_header(self.text),
            'encoding': 'base64'
        }

@dataclass
class HARResponse:
    status: int
    statusText: str
    httpVersion: str
    cookies: List[Dict[str, Any]]
    headers: List[Dict[str, Any]]
    content: HARContent
    redirectURL: str
    headersSize: int
    bodySize: int

    def json_data(self) -> Dict[str, Any]:
        return {
            'status': self.status,
            'statusText': self.statusText,
            'httpVersion': self.httpVersion,
            'cookies': [cookie.json_data() for cookie in self.cookies],
            'headers': [header.json_data() for header in self.headers],
            'content': self.content.json_data(),
            'redirectURL': self.redirectURL,
            'headersSize': self.headersSize,
            'bodySize': self.bodySize
        }

@dataclass
class HARTimings:
    send: datetime.timedelta
    receive: datetime.timedelta
    wait: datetime.timedelta
    connect: datetime.timedelta
    ssl: datetime.timedelta

    def total_seconds(self) -> int:
        return self.send.total_seconds() \
            + self.receive.total_seconds() \
            + self.wait.total_seconds() \
            + self.connect.total_seconds() \
            + self.ssl.total_seconds()

    def json_data(self) -> Dict[str, Any]:
        return {
            'send': 1000 * self.send.total_seconds(),
            'receive': 1000 * self.receive.total_seconds(),
            'wait': 1000 * self.wait.total_seconds(),
            'connect': 1000 * self.connect.total_seconds(),
            'ssl': 1000 * self.ssl.total_seconds(),
        }

@dataclass
class HAREntry:
    startedDateTime: datetime.datetime
    request: HARRequest
    response: HARResponse
    timings: HARTimings
    comment: str

    def json_data(self) -> Dict[str, Any]:
        data = {
            'startedDateTime': self.startedDateTime.isoformat(),
            'time': 1000 * self.timings.total_seconds(),
            'request': self.request.json_data(),
            'response': self.response.json_data(),
            'cache': {},
            'timings': self.timings.json_data(),
        }
        if self.comment is not None:
            data.comment = self.comment
        return data

@dataclass
class HAR:
    version: str
    creator: HARCreator
    entries: List[HAREntry]

    def json_data(self) -> Dict[str, Any]:
        return {
            'log': {
                'version': self.version,
                'creator': self.creator.json_data(),
                'entries': [entry.json_data() for entry in self.entries]
            }
        }

def make_name_value(xs: Dict[bytes, List[bytes]]) -> List[HARNameValue]:
    return list(flatten(((HARNameValue(decode_header(name), decode_header(v)) for v in value) for name, value in xs.items())))
