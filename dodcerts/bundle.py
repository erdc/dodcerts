import os

from pkg_resources import resource_filename

def where():
    """get the filepath of the DoD Certificate chain as a PEM bundle

    Returns:
        the filepath of the DoD Certificate chain as a PEM bundle
    """
    return os.getenv('DOD_CA_CERTS_PEM_PATH', resource_filename(__name__, 'dod-ca-certs.pem'))
