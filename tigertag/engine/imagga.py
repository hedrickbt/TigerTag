import argparse
import logging
import os
import sys
import time
from http.client import HTTPConnection  # py3

import requests
from requests.auth import HTTPBasicAuth

from tigertag.engine import Engine
from tigertag.engine import EngineListener
from tigertag.util import calc_hash
from tigertag.util import str2bool

logger = logging.getLogger(__name__)


class ArgumentException(Exception):
    pass


class ImaggaEngine(Engine):
    FILE_TYPES = ['png', 'jpg', 'jpeg', 'gif']

    def __init__(self, name, enabled, tries=5):
        super().__init__(name, enabled)
        self.prefix = 'tti'
        self.tries = tries

    def upload_image(self, auth, image_path):
        upload_id = None
        if not os.path.isfile(image_path):
            raise ArgumentException('Invalid image path')

        # Open the desired file
        with open(image_path, 'rb') as image_file:
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
                if 'result' not in content_response.json():
                    if current_try >= self.tries:
                        logging.warn('Failed to upload {} after {} tries.'.format(image_path, self.tries))
                        raise KeyError('result not found in {}'.format(content_response))
                    else:
                        logging.debug('Failed to upload {} try {} of {}.'.format(image_path, current_try, self.tries))
                        time.sleep(current_try * 2)
                        current_try = current_try + 1
                else:
                    success = True
                    uploaded_file = content_response.json()['result']

                    # Get the upload id of the uploaded file
                    upload_id = uploaded_file['upload_id']
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
        tagging_response = requests.get(
            '%s/tags' % self.props['API_URL'],
            auth=auth,
            params=tagging_query)

        return tagging_response.json()

    def calc_tag_name(self, tag_name):
        return '{}_{}'.format(self.prefix, tag_name)

    def tag(self, path):
        if 'API_KEY' not in self.props or 'API_SECRET' not in self.props:
            raise ArgumentException('You haven\'t set your API credentials.')

        auth = HTTPBasicAuth(self.props['API_KEY'], self.props['API_SECRET'])

        language = 'en' if 'LANGUAGE' not in self.props else self.props['LANGUAGE']
        verbose = False if 'VERBOSE' not in self.props else str2bool(self.props['VERBOSE'])

        upload_id = self.upload_image(auth, path)
        tag_result = self.imagga_tag_api(auth, upload_id, True, verbose, language)

        file_hash = calc_hash(path)
        tag_resonse = {
            'file_path': path,
            'file_hash': file_hash,
            'tags': {},
        }
        if 'result' in tag_result and 'tags' in tag_result['result']:
            for tag_item in tag_result['result']['tags']:
                new_tag = self.calc_tag_name(tag_item['tag']['en'])
                tag_resonse['tags'][new_tag] = {
                    'confidence': tag_item['confidence']
                }
        return tag_resonse

    def run(self):
        if 'API_KEY' not in self.props or 'API_SECRET' not in self.props:
            raise ArgumentException('You haven\'t set your API credentials.')

        tag_input = self.props['INPUT_LOCATION']
        if os.path.isdir(tag_input):
            images = [filename for filename in os.listdir(tag_input)
                      if os.path.isfile(os.path.join(tag_input, filename)) and
                      filename.split('.')[-1].lower() in ImaggaEngine.FILE_TYPES]

            images_count = len(images)
            for iterator, image_file in enumerate(images):
                image_path = os.path.join(tag_input, image_file)
                logging.info('[%s / %s] %s uploading' %
                             (iterator + 1, images_count, image_path))
                tag_result = self.tag(image_path)
                for listener in self.listeners:
                    listener.on_tags(self, tag_result)
        else:
            raise ArgumentException(
                'The input directory does not exist: %s' % tag_input)


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
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    args = parse_arguments()

    api_key = os.environ['IMAGGA_API_KEY']
    api_secret = os.environ['IMAGGA_API_SECRET']
    api_url = 'https://api.imagga.com/v2'

    en = ImaggaEngine('ImaggaEngine', True)
    en.props['API_KEY'] = api_key
    en.props['API_SECRET'] = api_secret
    en.props['API_URL'] = api_url
    en.props['INPUT_LOCATION'] = args.input[0]
    en.props['LANGUAGE'] = str(args.language)
    en.props['VERBOSE'] = str(args.verbose)
    el = EngineListener()
    el.on_tags = lambda engine, tag_info: print('{}: {}'.format(tag_info['file_path'], tag_info))
    en.listeners.append(el)
    logging.info('Tagging images started')
    en.run()
    logging.info('Tagging images complete')


if __name__ == '__main__':
    main()
