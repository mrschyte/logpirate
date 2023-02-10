from dataclasses import dataclass 
from typing import Any, Dict, List

import re

@dataclass
class Request:
    method: bytes
    path: bytes
    version: bytes

    headers: Dict[bytes, List[bytes]]
    cookies: Dict[bytes, List[bytes]]
    body: bytes

    def parse(request: bytes):
        lines = (line for line in request.split(b'\r\n'))
        method, path, version = re.split(r'\s+'.encode('ascii'), next(lines), 2)

        headers = {}
        for line in lines:
            if line == b'' or line == None:
                break
            name, value = re.split(r'\s*:\s*'.encode('ascii'), line, 1)
            name = name.lower()
            if name not in headers:
                headers[name] = []
            headers[name].append(value)

        cookies = {}

        if b'cookie' in headers:
            for header in headers[b'cookie']:
                for cookie in re.split(r'\s*;\s*'.encode('ascii'), header):
                    name, value = re.split(r'\s*=\s*'.encode('ascii'), cookie, 1)
                    if name not in cookies:
                        cookies[name] = []
                    cookies[name].append(value)

        body = b''.join(lines)

        return Request(method, path, version, headers, cookies, body)

@dataclass
class Response:
    version: bytes
    status: int
    message: bytes

    headers: dict[bytes, list[bytes]]
    cookies: dict[bytes, list[bytes]]
    body: bytes

    def parse(response: bytes):
        lines = (line for line in response.split(b'\r\n'))
        version, status, message = re.split(r'\s+'.encode('ascii'), next(lines), 2)

        headers = {}
        for line in lines:
            if line == b'' or line == None:
                break
            name, value = re.split(r'\s*:\s*'.encode('ascii'), line, 1)
            name = name.lower()
            if name not in headers:
                headers[name] = []
            headers[name].append(value)

        cookies = {}

        if b'cookie' in headers:
            for header in headers[b'cookie']:
                for cookie in re.split(r'\s*;\s*'.encode('ascii'), header):
                    name, value = re.split(r'\s*=\s*'.encode('ascii'), cookie, 1)
                    if name not in cookies:
                        cookies[name] = []
                    cookies[name].append(value)

        body = b''.join(lines)
        return Response(version, status, message, headers, cookies, body)
