import os.path

def where():
    """get the filepath of the DoD Certificate chain as a PEM bundle

    Returns:
        the filepath of the DoD Certificate chain as a PEM bundle
    """
    return os.path.join(os.path.dirname(__file__), 'dod-ca-certs.pem')