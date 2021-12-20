import json
import logging
import os

import yaml
from compreface import CompreFace
from compreface.collections import FaceCollection
from compreface.collections.face_collections import Subjects
from compreface.service import RecognitionService

from tigertag.engine import Engine
from tigertag.engine import TagInfo
from tigertag.util import create_scaled_image

logger = logging.getLogger(__name__)

# https://pythonawesome.com/compreface-open-source-face-recognition-system-from-exadel/
# keep image size to less than 5M
#       bytes / W px / 24 bpp * 8 bits / 0.1 jpg comp = H px
# ex: 5242880 / 5000 / 24     *	8      / 0.1	      = 3495.25333333333
MAX_SHORT_SIDE = 1000
MIN_CONFIDENCE = 85  # 0-100


class ComprefaceEngine(Engine):
    FILE_TYPES = ['png', 'jpg', 'jpeg', 'gif', 'ico', 'bmp', 'tif', 'tiff']

    def __init__(self, name, prefix, enabled, tries=5, min_confidence=MIN_CONFIDENCE):
        super().__init__(name, prefix, enabled)
        self.tries = tries
        self.min_confidence = min_confidence
        self.uploaded_faces = False
        self.faces_folder = None
        self.faces_config_file = None
        self.faces_config = None
        self.api_url = None
        self.api_port = None
        self.compre_api: CompreFace = None
        self.compre_recognition: RecognitionService = None
        self.compre_face_collection: FaceCollection = None
        self.compre_subjects: Subjects = None

    def _setup_compre_api(self):
        if self.compre_api is None:
            self.api_url = self.get_prop('API_URL')
            self.api_port = self.get_prop('API_PORT')
            self.compre_api = CompreFace(self.api_url, self.api_port)
            self.compre_recognition = self.compre_api.init_face_recognition(self.get_prop('API_KEY'))
            self.compre_face_collection = self.compre_recognition.get_face_collection()
            self.compre_subjects = self.compre_recognition.get_subjects()

    def delete_all_faces(self):
        self._setup_compre_api()
        self.compre_subjects.delete_all()

    def upload_faces(self) -> dict:
        uploaded = 0
        self._setup_compre_api()
        self.faces_folder = self.get_prop('FACES_FOLDER')
        self.faces_config_file = self.get_prop('FACES_CONFIG')
        with open(self.faces_config_file, 'r') as file:
            self.faces_config = yaml.safe_load(file)

        for face in self.faces_config['faces']:
            for image in face['images']:
                uploaded += 1
                face_image_file_name = os.path.normpath(os.path.join(
                    self.faces_folder, image['name']
                ))
                face_tag = face['tag']
                logger.debug(f'Uploading face {face_image_file_name} for {face_tag}')
                self.compre_face_collection.add(image_path=face_image_file_name, subject=face_tag)
        self.uploaded_faces = True
        subjects = sorted(self.compre_subjects.list()['subjects'])
        return {
            'subjects': subjects,
            'uploaded': uploaded,
        }

    def tag(self, path: str, temp: str = None, ext_id: str = None):
        if not self.uploaded_faces:
            self.delete_all_faces()
            self.upload_faces()
        tag_path = path if temp is None else temp

        logger.info('Tagging {}'.format(tag_path))
        scaled_image_path = create_scaled_image(tag_path, MAX_SHORT_SIDE)
        tag_result = None
        try:
            # This call below can leave the file open if there is an exception - which will
            # prevent the os.remove call from completing, throw an exception, and the application
            # will stop.
            # tag_result = self.compre_recognition.recognize(image_path=scaled_image_path)
            image_bytes: bytes = None
            with open(scaled_image_path, 'rb') as image:
                image_bytes = image.read()
            attempt = 1
            success = False
            while attempt <= self.tries and not success:
                try:
                    tag_result = self.compre_recognition.recognize(image_path=image_bytes)
                    success = True
                except json.decoder.JSONDecodeError:
                    logger.warning('Unable to tag {} try {} of {}.'.format(path, attempt, self.tries))
                    attempt += 1
            if attempt > self.tries:
                logger.warning('Failed to tag {} after {} tries.'.format(path, self.tries))
        finally:
            os.remove(scaled_image_path)

        tag_response: TagInfo = None
        if tag_result is not None and 'result' in tag_result:
            tags = {}
            for result in tag_result['result']:
                if 'subjects' in result:
                    for subject in result['subjects']:
                        new_tag = self.calc_tag_name(subject['subject'])
                        confidence = subject['similarity'] * 100  # 0-100 instead of 0-1
                        if confidence > self.min_confidence:
                            if new_tag in tags:
                                if confidence > tags[new_tag]['confidence']:
                                    tags[new_tag]['confidence'] = confidence
                            else:
                                tags[new_tag] = {
                                    'confidence': confidence
                                }
                        else:
                            logger.debug(f'Ignoring {new_tag} tag due to {confidence} confidence which is '
                                         f'lower than {self.min_confidence} for {path}.')
            tag_response = TagInfo(path, tags)
        else:
            tag_response = TagInfo(path, {})

        for listener in self.listeners:
            listener.on_tags(self, tag_response, ext_id)
        return tag_response
