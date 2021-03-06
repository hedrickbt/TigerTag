import argparse
import logging
import os
import sys
import time

import requests
from requests.auth import HTTPBasicAuth

from tigertag import ArgumentException
from tigertag.engine import Engine
from tigertag.engine import EngineListener
from tigertag.engine import TagInfo
from tigertag.scanner import ScannerListener
from tigertag.scanner.directory import DirectoryScanner
from tigertag.util import create_scaled_image
from tigertag.util import str2bool

logger = logging.getLogger(__name__)
MAX_SHORT_SIDE = 300


class ImaggaEngine(Engine):
    FILE_TYPES = ['png', 'jpg', 'jpeg', 'gif']

    def __init__(self, name, prefix, enabled, tries=5):
        super().__init__(name, prefix, enabled)
        self.tries = tries

    def upload_image(self, auth, image_path):
        upload_id = None
        if not os.path.isfile(image_path):
            raise ArgumentException(f'Invalid image path {image_path}')

        scaled_image_path = create_scaled_image(image_path, MAX_SHORT_SIDE)

        # Open the desired file
        with open(scaled_image_path, 'rb') as image_file:
            current_try = 1
            success = False
            while not success and current_try <= self.tries:
                content_response = requests.post(
                    '%s/uploads' % self.props['API_URL'],
                    auth=auth,
                    files={'image': image_file})

                # Example /uploads response:
                #    {
                #      "result": {
                #        "upload_id": "i05e132196706b94b1d85efb5f3SaM1j"
                #      },
                #      "status": {
                #        "text": "",
                #        "type": "success"
                #      }
                #    }
                logger.debug(f'Response status: {content_response.status_code}')
                if content_response.status_code == 504 or 'result' not in content_response.json():
                    if current_try >= self.tries:
                        logger.warning('Failed to upload {} as {} after {} tries.'.format(image_path, scaled_image_path, self.tries))
                        raise KeyError('result not found in {}'.format(content_response))
                    else:
                        logger.warning('Unable to upload {} as {} try {} of {}.'.format(
                            image_path, scaled_image_path, current_try, self.tries))
                        time.sleep(current_try * 2)
                        current_try = current_try + 1
                else:
                    logger.debug('Uploaded {} as {} after {} tries.'.format(
                        image_path, scaled_image_path, current_try))
                    success = True
                    uploaded_file = content_response.json()['result']

                    # Get the upload id of the uploaded file
                    upload_id = uploaded_file['upload_id']
        os.remove(scaled_image_path)
        return upload_id

    def imagga_tag_api(self, auth, image, upload_id=False, verbose=False, language='en'):
        # Using the content id and the content parameter,
        # make a GET request to the /tagging endpoint to get
        # image tags
        tagging_query = {
            'image_upload_id' if upload_id else 'image_url': image,
            'verbose': verbose,
            'language': language
        }
        result = {}
        current_try = 1
        success = False
        while not success and current_try <= self.tries:
            tagging_response = requests.get(
                '%s/tags' % self.props['API_URL'],
                auth=auth,
                params=tagging_query
            )

            logger.debug(f'Response status: {tagging_response.status_code}')
            tagging_json = tagging_response.json()
            if tagging_response.status_code == 504 or 'result' not in tagging_json or \
                    'tags' not in tagging_json['result']:
                if current_try >= self.tries:
                    logger.warning('Failed to tag {} after {} tries.'.format(image, self.tries))
                    raise KeyError('result not found in {}'.format(tagging_response))
                else:
                    logger.warning('Unable to tag {} try {} of {}.'.format(image, current_try, self.tries))
                    time.sleep(current_try * 2)
                    current_try += 1
            else:
                logger.debug('Tagged {} after {} tries.'.format(image, current_try))
                success = True
                result = tagging_json
        return result

    def tag(self, path: str, temp: str = None, ext_id: str = None):
        tag_path = path if temp is None else temp
        if 'API_KEY' not in self.props or 'API_SECRET' not in self.props:
            raise ArgumentException('You haven\'t set your API credentials.')

        auth = HTTPBasicAuth(self.props['API_KEY'], self.props['API_SECRET'])

        language = 'en' if 'LANGUAGE' not in self.props else self.props['LANGUAGE']
        verbose = False if 'VERBOSE' not in self.props else str2bool(self.props['VERBOSE'])

        logger.info('Tagging {}'.format(tag_path))
        upload_id = self.upload_image(auth, tag_path)
        tag_result = self.imagga_tag_api(auth, upload_id, True, verbose, language)

        tag_response: TagInfo = TagInfo(path, None)
        if 'result' in tag_result and 'tags' in tag_result['result']:
            tags = {}
            for tag_item in tag_result['result']['tags']:
                new_tag = self.calc_tag_name(tag_item['tag']['en'])
                tags[new_tag] = {
                    'confidence': tag_item['confidence']
                }
            tag_response = TagInfo(path, tags)

        for listener in self.listeners:
            listener.on_tags(self, tag_response, ext_id)
        return tag_response


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Tags images in a folder')

    parser.add_argument(
        'input',
        metavar='<input>',
        type=str,
        nargs=1,
        help='The input - a folder containing images')

    parser.add_argument(
        '--language',
        type=str,
        default='en',
        help='The language of the output tags')

    parser.add_argument(
        '--verbose',
        type=lambda x: bool(str2bool(x)),
        default=False,
        help='Whether to use verbose mode')

    args = parser.parse_args()
    return args


def main():
    #HTTPConnection.debuglevel = 1
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(name)s : %(funcName)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    args = parse_arguments()

    api_key = os.environ['IMAGGA_API_KEY']
    api_secret = os.environ['IMAGGA_API_SECRET']
    api_url = 'https://api.imagga.com/v2'

    en = ImaggaEngine('ImaggaEngine', True)
    en.props['API_KEY'] = api_key
    en.props['API_SECRET'] = api_secret
    en.props['API_URL'] = api_url
    en.props['LANGUAGE'] = str(args.language)
    en.props['VERBOSE'] = str(args.verbose)

    el = EngineListener()
    el.on_tags = lambda engine, tag_info: print('{}: {}'.format(tag_info.path, tag_info))
    en.listeners.append(el)

    s = DirectoryScanner('directory_scanner', True)
    s.props['PATH'] = args.input[0]
    sl = ScannerListener()
    sl.on_file = lambda scanner, file_info: en.tag(file_info.path)
    s.listeners.append(sl)

    logger.info('Tagging images started')
    s.scan()
    logger.info('Tagging images complete')


if __name__ == '__main__':
    main()
