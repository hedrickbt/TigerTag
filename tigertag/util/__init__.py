import hashlib
import logging
import os
import shutil
import tempfile

from PIL import Image

logger = logging.getLogger(__name__)


def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


def calc_hash(file_path):
    h = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while True:
            # Reading is buffered, so we can read smaller chunks.
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def create_temporary_copy(image_path):
    root, ext = os.path.splitext(image_path)
    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=True)
    tmp.close()
    shutil.copy2(image_path, tmp.name)
    return tmp.name


def create_scaled_image(image_path, max_short_side):
    # https://docs.imagga.com/#color-palette-deterministic
    # The API doesn't need more that 300px on the shortest side to provide you
    # with the same great results.
    result = None
    need_scale = False
    old_bytes = os.stat(image_path).st_size
    with Image.open(image_path) as img:
        width, height = img.size
        if width < height and width > max_short_side:
            new_width = max_short_side
            percent = new_width/width
            new_height = int((float(height) * float(percent)))
            need_scale = True
        elif width > height and height > max_short_side:
            new_height = max_short_side
            percent = new_height / height
            new_width = int((float(width) * float(percent)))
            need_scale = True

        scaled_image_path = create_temporary_copy(image_path)
        if need_scale:
            img = img.resize((new_width, new_height), Image.ANTIALIAS)
            img.save(scaled_image_path)
            new_bytes = os.stat(scaled_image_path).st_size
            logger.debug(f'Resizing {image_path} as {scaled_image_path} from '
                         f'({width},{height}) to ({new_width},{new_height}) with old/new bytes '
                         f'{old_bytes}/{new_bytes}.')
        else:
            logger.debug(f'Using original {image_path} as {scaled_image_path} '
                         f'({width},{height}) with {old_bytes} bytes.')
        return scaled_image_path