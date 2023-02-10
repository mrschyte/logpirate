from lxml import etree, objectify
from logpirate.model.http import Request, Response
from logpirate.model.har import *
from logpirate.util import decode_header

import base64
import click
import json
import logging
import urllib.parse

def get_decoded_value(element):
    if element.attrib['base64']:
        return base64.b64decode(element.text)
    return element.text.encode('ascii')

def get_header_value(element, header, default):
    return decode_header(element.headers.get(header, [default])[0])

def make_har_entry(item):
    request_bytes = get_decoded_value(item.request)
    response_bytes = get_decoded_value(item.response)

    request = Request.parse(request_bytes)
    response = Response.parse(response_bytes)

    url = urllib.parse.urlparse(request.path)
    query = urllib.parse.parse_qs(url.query)

    mimeType = get_header_value(response, b'content-type', b''),
    redirectURL = get_header_value(response, b'location', b''),

    return HAREntry(
        startedDateTime=dateutil.parser.parse(item.time.text),
        request=HARRequest(
            method=decode_header(request.method),
            url=item.url.text,
            httpVersion=decode_header(request.version),
            cookies=make_name_value(request.cookies),
            headers=make_name_value(request.headers),
            queryString=make_name_value(query),
            headersSize=len(request_bytes) - len(request.body),
            bodySize=len(request.body)
        ),
        response=HARResponse(
            status=int(response.status),
            statusText=decode_header(response.message),
            httpVersion=decode_header(response.version),
            cookies=make_name_value(response.cookies),
            headers=make_name_value(response.headers),
            content=HARContent(
                size=len(response.body),
                mimeType=mimeType,
                text=base64.b64encode(response.body)
            ),
            redirectURL=redirectURL,
            headersSize=len(response_bytes) - len(response.body),
            bodySize=len(response.body)
        ),
        # XXX: dummy values as the log file doesn't contain timings
        timings=HARTimings(
            send=datetime.timedelta(milliseconds=1),
            receive=datetime.timedelta(milliseconds=1),
            wait=datetime.timedelta(milliseconds=1),
            connect=datetime.timedelta(milliseconds=1),
            ssl=datetime.timedelta(milliseconds=1)
        ),
        comment=item.comment.text
    )

def make_har(root):
    entries = [make_har_entry(item) for item in root.item]
    return HAR(
        version='1.2',
        creator=HARCreator(
            name='logpirate',
            version='0.1',
            comment='logpirate'
        ),
        entries=entries
    )


@click.command()
@click.option('--loglevel', type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']), default='INFO')
@click.argument('burplog')
@click.argument('harfile')
def main(loglevel, burplog, harfile):
    logging.basicConfig(level=getattr(logging, loglevel), format='%(asctime)s %(message)s')

    tree = objectify.parse(burplog)
    root = tree.getroot()
    har = make_har(root)

    with open(harfile, 'w') as fp:
        json.dump(har.json_data(), fp)
        logging.info('Saved %d request/response pairs', len(har.entries))
        logging.info('%d bytes written', fp.tell())

if __name__ == '__main__':
    main()
