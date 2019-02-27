import os.path
import shutil
import sys

import logging
import tarfile
import zipfile

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import Certificate, load_der_x509_certificate, load_pem_x509_certificate
from cryptography.x509.name import NameOID
from datetime import datetime
from urllib.request import urlopen

from .bundle import where

log = logging.getLogger('dod-certs')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
log.addHandler(ch)

certs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'certs')

def describe_cert(cert):
    """extract and format certification information as comment

    Args:
        cert(cryptography.x509.Certificate, required):
            a x509 formatted certificate to process

    Returns:
        a string that contains the certification information
    """
    assert isinstance(cert, Certificate)
    info = (
        "\n"
        "# Subject: {}\n"
        "# Issued by: {} {}\n"
        "# Signed with: {}\n"
        "# Expires: {}\n"
    ).format(
        cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value,
        *[cert.issuer.get_attributes_for_oid(oid)[0].value
          for oid in [NameOID.ORGANIZATION_NAME, NameOID.ORGANIZATIONAL_UNIT_NAME, NameOID.COMMON_NAME]],
        cert.not_valid_after,
    )

    return info


def download_resources(urls):
    """retrieve, place, and extract resources from archive (if necessary) into `certs` directory

    Args:
        urls(iterable, required):
            an iterable of urls (e.g. https://militarycac.org/maccerts/AllCerts.zip) as strings
    """

    # clear the certs directory
    if os.path.exists(certs_dir):
        assert os.path.isdir(certs_dir)
        if len(os.listdir(certs_dir)) > 0:
            shutil.rmtree(certs_dir)
    if not os.path.exists(certs_dir):
        os.mkdir(certs_dir)

    if isinstance(urls, str):
        urls = [urls, ]

    # process the resources
    cert_exts = ['cer', 'crt', 'pem']
    for url in urls:
        assert isinstance(url, str)
        if not url:
            continue
        log.info('Downloading resource: {}'.format(url))
        response = urlopen(url)
        fpath = os.path.join(certs_dir, os.path.basename(url))
        with open(fpath, 'wb') as f:
            f.write(response.read())
        log.info('Resource written to: {}'.format(fpath))

        if tarfile.is_tarfile(fpath):
            with open(fpath, 'rb') as f:
                try:
                    tar = tarfile.open(mode='r:*', fileobj=f)
                    for file in tar:
                        if any([file.name.endswith(ext) for ext in cert_exts]):
                            tar.extract(member=file, path=certs_dir)
                    tar.close()
                except tarfile.TarError as e:
                    log.warning('Unable to extract resource: {}'.format(fpath))
            os.remove(fpath)
            log.info('Extracted archive and removed: {}'.format(fpath))
        elif zipfile.is_zipfile(fpath):
            try:
                zip = zipfile.ZipFile(fpath)
                for file in zip.filelist:
                    if any([file.filename.endswith(ext) for ext in cert_exts]):
                        zip.filename = os.path.basename(zip.filename)
                        zip.extract(member=file, path=certs_dir)
                zip.close()
                os.remove(fpath)
                log.info('Extracted zip and removed: {}'.format(fpath))
            except tarfile.TarError as e:
                log.warning('Unable to extract resource: {}'.format(fpath))


def create_pem_bundle(urls=None, filepath=None):
    """create a PEM formatted certificate bundle from the resources in the `certs` directory

    Args:
        urls(iterable, optional, default=None):
            passed to `download_resources` if specified, else use contents of `certs` directory
        filepath(str, optional, default=None):
            location of newly created pem bundle file; defaulted to `where` location
    """
    filepath = filepath or where()
    if urls is not None:
        download_resources(urls)

    # create empty bytes stream
    pem_bundle = "# Bundle Created: {} \n".format(datetime.now()).encode()
    # get file list
    files = sorted(os.listdir(certs_dir))
    # process CAs first then Roots
    for type in ['ca', 'root']:
        for file in files:
            fpath = os.path.join(certs_dir, file)
            if file.lower().find(type) > -1 and os.path.isfile(fpath):
                with open(fpath, 'rb') as f:
                    contents = f.read()
                    try:
                        cert = load_der_x509_certificate(contents, backend=default_backend())
                    except ValueError:
                        try:
                            cert = load_pem_x509_certificate(contents, backend=default_backend())
                        except ValueError:
                            log.warning('Unable to load public key from: {}'.format(file))
                            continue
                    # add cert's info and public key in PEM format to the bytes stream
                    pem_bundle += describe_cert(cert).encode()
                    pem_bundle += cert.public_bytes(Encoding.PEM)

    with open(filepath, 'wb') as f:
        f.write(pem_bundle)
