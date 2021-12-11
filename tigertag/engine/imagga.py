import argparse
import json
import logging
import os
import time

import requests
from requests.auth import HTTPBasicAuth

from tigertag.engine import Engine
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
                    if current_try > self.tries:
                        raise KeyError('result not found in {}'.format(content_response))
                    else:
                        time.sleep(current_try * 2)
                        current_try = current_try + 1
                else:
                    success = True
                    uploaded_file = content_response.json()['result']

                    # Get the upload id of the uploaded file
                    upload_id = uploaded_file['upload_id']
        return upload_id

    def tag_image(self, auth, image, upload_id=False, verbose=False, language='en'):
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

    # def extract_colors(self, auth, image, upload_id=False):
    #     colors_query = {
    #         'image_upload_id' if upload_id else 'image_url': image,
    #     }
    #
    #     colors_response = requests.get(
    #         '%s/colors' % self.props['API_URL'],
    #         auth=auth,
    #         params=colors_query)
    #
    #     return colors_response.json()

    def calc_tag_name(self, tag_name):
        return '{}_{}'.format(self.prefix, tag_name)

    def run(self):
        if 'API_KEY' not in self.props or 'API_SECRET' not in self.props:
            raise ArgumentException('You haven\'t set your API credentials.')

        auth = HTTPBasicAuth(self.props['API_KEY'], self.props['API_SECRET'])

        tag_input = self.props['INPUT_LOCATION']
        tag_output = self.props['OUTPUT_LOCATION']
        language = 'en' if 'LANGUAGE' not in self.props else self.props['LANGUAGE']
        verbose = False if 'VERBOSE' not in self.props else str2bool(self.props['VERBOSE'])
        # merged_output = False if 'MERGED_OUTPUT' not in self.props else str2bool(self.props['MERGED_OUTPUT'])
        # include_colors = False if 'INCLUDE_COLORS' not in self.props else str2bool(self.props['INCLUDE_COLORS'])

        results = {}
        if os.path.isdir(tag_input):
            images = [filename for filename in os.listdir(tag_input)
                      if os.path.isfile(os.path.join(tag_input, filename)) and
                      filename.split('.')[-1].lower() in ImaggaEngine.FILE_TYPES]

            images_count = len(images)
            for iterator, image_file in enumerate(images):
                image_path = os.path.join(tag_input, image_file)
                print('[%s / %s] %s uploading' %
                      (iterator + 1, images_count, image_path))
                # try:
                upload_id = self.upload_image(auth, image_path)
                # except IndexError:
                #    continue
                # except KeyError:
                #    continue
                # except ArgumentException:
                #    continue

                tag_result = self.tag_image(auth, upload_id, True, verbose, language)

                # Long term this needs to go unless there is some sort of setting to write the files
                with open(
                        os.path.join(tag_output, 'result_%s.json' % image_file),
                        'wb') as results_file:
                    result_json = json.dumps(
                        tag_result, ensure_ascii=False, indent=4).encode('utf-8')
                    results_file.write(result_json)

                if len(self.listeners) > 0:
                    file_hash = calc_hash(image_path)
                    tag_resonse = {
                        'file_path': image_path,
                        'file_hash': file_hash,
                        'tags': {},
                    }
                    if 'result' in tag_result and 'tags' in tag_result['result']:
                        for tag_item in tag_result['result']['tags']:
                            new_tag = self.calc_tag_name(tag_item['tag']['en'])
                            tag_resonse['tags'][new_tag] = {
                                'confidence': tag_item['confidence']
                            }
                    for listener in self.listeners:
                        listener.on_tags(self, tag_resonse)

                # results[image_file] = tag_result
                # if not include_colors:
                #     results[image_file] = tag_result
                # else:
                #     colors_result = self.extract_colors(auth, upload_id, True)
                #     results[image_file] = {
                #         'tagging': tag_result,
                #         'colors': colors_result
                #     }
                # print('[%s / %s] %s tagged' %
                #       (iterator + 1, images_count, image_path))
        else:
            raise ArgumentException(
                'The input directory does not exist: %s' % tag_input)

        if not os.path.exists(tag_output):
            os.makedirs(tag_output)
        elif not os.path.isdir(tag_output):
            raise ArgumentException(
                'The output folder must be a directory')

        # if merged_output:
        #     with open(
        #             os.path.join(tag_output, 'results.json'),
        #             'wb') as results_file:
        #         results_file.write(
        #             json.dumps(
        #                 results, ensure_ascii=False, indent=4).encode('utf-8'))
        # else:
        #     for image, result in results.items():
        #         with open(
        #                 os.path.join(tag_output, 'result_%s.json' % image),
        #                 'wb') as results_file:
        #             results_file.write(
        #                 json.dumps(
        #                     result, ensure_ascii=False, indent=4).encode('utf-8'))

        print('Done')


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
        'output',
        metavar='<output>',
        type=str,
        nargs=1,
        help='The output - a folder to output the results')

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

    # parser.add_argument(
    #     '--merged-output',
    #     type=lambda x: bool(str2bool(x)),
    #     default=False,
    #     help='Whether to generate a single output file')

    # parser.add_argument(
    #     '--include-colors',
    #     type=lambda x: bool(str2bool(x)),
    #     default=False,
    #     help='Whether to do color extraction on the images too')

    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()

    api_key = os.environ['IMAGGA_API_KEY']
    api_secret = os.environ['IMAGGA_API_SECRET']
    api_url = 'https://api.imagga.com/v2'

    en = ImaggaEngine('ImaggaEngine', True)
    en.props['API_KEY'] = api_key
    en.props['API_SECRET'] = api_secret
    en.props['API_URL'] = api_url
    en.props['INPUT_LOCATION'] = args.input[0]
    en.props['OUTPUT_LOCATION'] = args.output[0]
    en.props['LANGUAGE'] = str(args.language)
    en.props['VERBOSE'] = str(args.verbose)
    # en.props['MERGED_OUTPUT'] = str(args.merged_output)
    # en.props['INCLUDE_COLORS'] = str(args.include_colors)

    print('Tagging images started')
    en.run()


if __name__ == '__main__':
    main()
