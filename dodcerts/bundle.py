import os

from importlib.resources import files


def where():
    """get the filepath of the DoD Certificate chain as a PEM bundle

    Returns:
        the filepath of the DoD Certificate chain as a PEM bundle
    """
    return os.getenv('DOD_CA_CERTS_PEM_PATH', files('dodcerts') / 'dod-ca-certs.pem')
