#!/usr/bin/env python
import hashlib
import pathlib
import shutil

from dodcerts.create import create_pem_bundle

# certificate resources to bundle
urls = ['https://militarycac.org/maccerts/AllCerts.zip',]
dir = pathlib.Path(__file__).parent

# create new bundle and hash
bundlepath = create_pem_bundle(destination=(dir / 'my_bundle.pem').as_posix(), urls=urls)
hash = hashlib.sha256()
with open(bundlepath, 'r') as file:
    # skip timestamp line
    file.readline()
    for l in file.readlines():
        hash.update(l.encode())
newsignature = hash.hexdigest()
print(newsignature)
# get old hash
hashpath = (dir / 'dod-ca-certs.hash').as_posix()
with open(hashpath, 'r') as file:
    oldsignature = file.read()
print(oldsignature)
# compare hashes
if newsignature != oldsignature:
    # overwrite existing bundle and hash
    with open(hashpath, 'w') as file:
        file.write(newsignature)
        shutil.move(bundlepath, (dir / '..' / 'dodcerts' / 'dod-ca-certs.pem').as_posix())
    print('update')
    exit(0)
else:
    exit(1)
