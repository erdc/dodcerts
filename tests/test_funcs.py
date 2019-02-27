import os
import shutil

import tarfile
import tempfile
import zipfile

from cryptography.hazmat.backends import default_backend
from cryptography.x509 import Certificate, load_der_x509_certificate
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
    with open(filepath, 'r') as f:
        assert f.readline().find('# Bundle Created: ') == 0
        assert f.readline().find('\n') == 0
        assert f.readline().find('# Subject: ') == 0
        assert f.readline().find('# Issued by: ') == 0
        assert f.readline().find('# Signed with: ') == 0
        assert f.readline().find('# Expires: ') == 0
        assert f.readline().find('-----BEGIN CERTIFICATE-----\n') == 0
        line = f.readline()
        while line is not '':
            last = line
            line = f.readline()
        assert last.find('-----END CERTIFICATE-----\n') == 0

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
                      '# Expires: 2041-06-14 17:17:27\n'

def test_download_resources():
    try:
        from dodcerts.create import download_resources
    except:
        assert False
    # copy file into certs directory to verify directory clearing
    fpath = Path(__file__).parent / 'input' / 'DoDRoot5.cer'
    certs_dir = Path(__file__).parent.parent / 'dodcerts' / 'certs'
    shutil.copy(fpath, certs_dir)

    assert certs_dir.exists()
    assert certs_dir.is_dir()
    assert len(os.listdir(certs_dir)) > 0

    download_resources('')
    assert certs_dir.is_dir()
    assert certs_dir.exists()
    assert len(os.listdir(certs_dir)) == 0

    # verify string input and single file
    download_resources(fpath.as_uri())
    assert len(os.listdir(certs_dir)) == 1

    # verify iterable input
    download_resources([fpath.as_uri(),])
    assert len(os.listdir(certs_dir)) == 1

    #import pdb; pdb.set_trace()
    with tempfile.TemporaryDirectory() as tmpdir:
        # verify zip file
        zippath = Path(tmpdir) / 'certs.zip'
        with zipfile.ZipFile(zippath, 'w') as zip:
            zip.write(fpath)
        download_resources([zippath.as_uri(),])
        assert len(os.listdir(certs_dir)) == 1

        # verify tar file
        tarpath = Path(tmpdir) / 'certs.tar'
        with tarfile.TarFile(tarpath, 'w') as tar:
            tar.add(fpath)
        download_resources([tarpath.as_uri(),])
        assert len(os.listdir(certs_dir)) == 1

def test_create_pem_bundle():
    try:
        from dodcerts.create import create_pem_bundle, download_resources
    except:
        assert False

    with tempfile.TemporaryDirectory() as tmpdir:
        # make bundle from test cert
        fpath = Path(os.path.dirname(__file__)) / 'input' / 'DoDRoot5.cer'
        bundlepath = Path(tmpdir) / 'dod-ca-certs.pem'

        create_pem_bundle(filepath=bundlepath, urls=[fpath.as_uri(),])
        assert bundlepath.exists()
        with open(bundlepath, 'r') as f:
            bundle_dt = datetime.strptime(f.readline(), '# Bundle Created: %Y-%m-%d %H:%M:%S.%f\n')
            span = datetime.now() - bundle_dt
            assert span.total_seconds() < 10.
