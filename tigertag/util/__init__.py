import hashlib


def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


def calc_digest(file_path):
    h = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while True:
            # Reading is buffered, so we can read smaller chunks.
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
