from hashlib import sha256


def hash_string(content_to_hash: str) -> str:
    """
    Returns the SHA256 hash of the content.
    :param content_to_hash: string t be hashed
    """
    sha = sha256()
    sha.update(content_to_hash.encode('UTF-8'))
    return sha.hexdigest()
