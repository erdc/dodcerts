import os
import shutil

import tarfile
import tempfile
import zipfile

from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_der_x509_certificate
from datetime import datetime
from pathlib import Path


def test_where():
    try:
        from dodcerts import where
    except:
        assert False
    filepath = where()
    assert filepath is not None
    filepath = Path(filepath)
    assert filepath.name == 'dod-ca-certs.pem'
    assert filepath.exists()
    with open(filepath, 'r') as f:
        assert f.readline().find('# Bundle Created: ') == 0
        assert f.readline().find('\n') == 0
        assert f.readline().find('# Subject: ') == 0
        assert f.readline().find('# Issued by: ') == 0
        assert f.readline().find('# Signed with: ') == 0
        assert f.readline().find('# Expires: ') == 0
        assert f.readline().find('-----BEGIN CERTIFICATE-----\n') == 0
        for line in f.readlines():
            last = line
        assert last.find('-----END CERTIFICATE-----\n') == 0

    env = os.getenv('DOD_CA_CERTS_PATH', None)
    os.environ['DOD_CA_CERTS_PEM_PATH'] = 'TEST'
    filepath = where()
    assert filepath == 'TEST'
    if env is not None:
        os.environ['DOD_CA_CERTS_PEM_PATH'] = env
    else:
        os.environ.pop('DOD_CA_CERTS_PEM_PATH')


def test_describe_cert():
    try:
        from dodcerts.create import describe_cert
    except:
        assert False
    fpath = Path(__file__).parent / 'input' / 'DoDRoot5.cer'
    with open(fpath, 'rb') as f:
        cert = load_der_x509_certificate(f.read(), backend=default_backend())
        res = describe_cert(cert)
        assert res == '\n' \
                      '# Subject: DoD Root CA 5\n' \
                      '# Issued by: U.S. Government DoD\n' \
                      '# Signed with: DoD Root CA 5\n' \
                      '# Expires: 2041-06-14 17:17:27+00:00\n'


def test_download_resources():
    try:
        from dodcerts.create import download_resources
    except:
        assert False
    fpath = Path(__file__).parent / 'input' / 'DoDRoot5.cer'

    with tempfile.TemporaryDirectory() as resource_dir:
        # verify string input and single file with specified destination
        assert len(os.listdir(resource_dir)) == 0
        assert download_resources(urls=fpath.resolve().as_uri(), destination=resource_dir) == resource_dir
        assert len(os.listdir(resource_dir)) == 1

    # verify iterable input
    resource_dir = download_resources(urls=[fpath.as_uri(),])
    assert len(os.listdir(resource_dir)) == 1
    shutil.rmtree(resource_dir)

    with tempfile.TemporaryDirectory() as archive_dir:
        # verify zip file
        zippath = Path(archive_dir) / 'certs.zip'
        with zipfile.ZipFile(zippath, 'w') as zip:
            zip.write(fpath)
        resource_dir = download_resources([zippath.as_uri(),])
        assert len(os.listdir(resource_dir)) == 1
        shutil.rmtree(resource_dir)

        # verify tar file
        tarpath = Path(archive_dir) / 'certs.tar'
        with tarfile.TarFile(tarpath, 'w') as tar:
            tar.add(fpath)
        resource_dir = download_resources([tarpath.as_uri()])
        assert len(os.listdir(resource_dir)) == 1
        shutil.rmtree(resource_dir)


def test_create_pem_bundle():
    try:
        from dodcerts.create import create_pem_bundle, download_resources
    except:
        assert False

    with tempfile.TemporaryDirectory() as tmpdir:
        # make bundle from test cert
        fpath = Path(os.path.dirname(__file__)) / 'input' / 'DoDRoot5.cer'
        bundlepath = Path(tmpdir) / 'dod-ca-certs.pem'

        env = os.environ.get('DOD_CA_CERTS_PEM_PATH', None)
        if env is not None:
            os.environ.pop('DOD_CA_CERTS_PEM_PATH')

        create_pem_bundle(destination=bundlepath.as_posix(), urls=[fpath.as_uri(),], set_env_var=False)
        assert bundlepath.exists()
        with open(bundlepath, 'r') as f:
            bundle_dt = datetime.strptime(f.readline(), '# Bundle Created: %Y-%m-%d %H:%M:%S.%f\n')
            span = datetime.now() - bundle_dt
            assert span.total_seconds() < 10.
        assert os.environ.get('DOD_CA_CERTS_PEM_PATH', None) is None

        res = create_pem_bundle(destination=bundlepath.as_posix(), urls=[fpath.as_uri(),], set_env_var=True)
        assert os.environ.get('DOD_CA_CERTS_PEM_PATH', None) == res

        if env is not None:
            os.environ['DOD_CA_CERTS_PEM_PATH'] = env
