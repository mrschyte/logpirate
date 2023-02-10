from types import GeneratorType
from typing import Any, Dict, List

def flatten(xs: List[Any]) -> List[Any]:
    for x in xs:
        if type(x) == list or isinstance(x, GeneratorType):
            for y in flatten(x):
                yield y
        else:
            yield x

def decode_header(header: bytes) -> str:
    return header.decode('ascii')
