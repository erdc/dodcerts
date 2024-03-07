import os
import sys

import logging
import tarfile
import tempfile
import zipfile

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import Certificate, load_der_x509_certificate, load_pem_x509_certificate
from cryptography.x509.name import NameOID
from datetime import datetime
from urllib.request import urlopen

log = logging.getLogger('dod-certs')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
log.addHandler(ch)

cert_exts = ['cer', 'crt', 'pem']


def describe_cert(cert):
    """extract and format certification information as comment

    Args:
        cert(cryptography.x509.Certificate, required):
            a x509 formatted certificate to process

    Returns:
        certification information as a string
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
        cert.not_valid_after_utc,
    )

    return info


def download_resources(urls, destination=None):
    """retrieve, place, and extract resources from archive (if necessary) into `certs` directory

    Args:
        urls(iterable, required):
            iterable of urls (e.g. https://militarycac.org/maccerts/AllCerts.zip) as strings
        destination(string, optional, default=None):
            location to which resources are downloaded; defaulted to a new temporary directory that must then be managed
            by the calling process

    Returns:
        path to the downloaded resources as a string
    """
    if destination is None:
        destination = tempfile.mkdtemp(prefix='certs_')
        log.info('Created temporary directory')
    if not os.path.exists(destination):
        os.mkdir(destination)
    assert os.path.isdir(destination)

    if isinstance(urls, str):
        urls = [urls, ]

    # process the resources
    for url in urls:
        assert isinstance(url, str)
        if not url:
            continue
        log.info('Downloading resource: {}'.format(url))
        response = urlopen(url)
        fpath = os.path.join(destination, os.path.basename(url))
        with open(fpath, 'wb') as f:
            f.write(response.read())
        log.info('Resource written to: {}'.format(fpath))

        if tarfile.is_tarfile(fpath):
            with open(fpath, 'rb') as f:
                try:
                    tar = tarfile.open(mode='r:*', fileobj=f)
                    for file in tar:
                        if any([file.name.endswith(ext) for ext in cert_exts]):
                            tar.extract(member=file, path=destination)
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
                        zip.extract(member=file, path=destination)
                zip.close()
                os.remove(fpath)
                log.info('Extracted zip and removed: {}'.format(fpath))
            except tarfile.TarError as e:
                log.warning('Unable to extract resource: {}'.format(fpath))
    return destination


def create_pem_bundle(destination, urls=None, resource_dir=None, set_env_var=True):
    """create a PEM formatted certificate bundle from the specified resources

    Args:
        destination(str, required):
            pathname for created pem bundle file
        urls(iterable, optional, default=None):
            passed to `download_resources` if specified, else the existing contents of `resource_dir` are processed;
            `urls` and/or `resource_dir` must be specified
        resource_dir(str, optional, default=None):
            location of resources to process; passed to `download_resources` along with `urls` if both specified, else
            a temporary location is utilized
        set_env_var(bool, optional, default=True):
            determines whether the `DOD_CA_CERTS_PEM_PATH` environmental variable is set with the value of created pem
            bundle pathname

    Returns:
        pathname of created pem bundle file
    """
    if resource_dir is not None:
        assert os.exists(resource_dir)
        assert os.is_dir(resource_dir)
    else:
        assert urls is not None  # `urls` or `resource_dir` must be specified

    if urls is not None:
        resource_dir = download_resources(urls, resource_dir)

    # create empty bytes stream
    pem_bundle = "# Bundle Created: {} \n".format(datetime.now()).encode()
    # get file list
    files = sorted(os.listdir(resource_dir))
    # process CAs first then Roots
    for type in ['ca', 'root']:
        for file in files:
            if any([file.endswith(ext) for ext in cert_exts]):
                fpath = os.path.join(resource_dir, file)
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
    destination = os.path.abspath(destination)
    with open(destination, 'wb') as f:
        f.write(pem_bundle)

    if set_env_var:
        os.environ['DOD_CA_CERTS_PEM_PATH'] = destination
        log.info('Set DOD_CA_CERTS_PEM_PATH environment variable')

    return destination
