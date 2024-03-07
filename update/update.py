#!/usr/bin/env python
import hashlib
import pathlib
import shutil

from dodcerts.create import create_pem_bundle

# certificate resources to bundle
urls = ['https://militarycac.org/maccerts/AllCerts.zip',]
this_dir = pathlib.Path(__file__).parent

# create new bundle and hash
bundle_path = create_pem_bundle(destination=(this_dir / 'my_bundle.pem').as_posix(), urls=urls)
new_bundle_hash = hashlib.sha256()
with open(bundle_path, 'r') as file:
    # skip timestamp line
    file.readline()
    for line in file.readlines():
        new_bundle_hash.update(line.encode())
new_signature = new_bundle_hash.hexdigest()
print(new_signature)

# get old hash
hash_path = (this_dir / 'dod-ca-certs.hash').as_posix()
with open(hash_path, 'r') as file:
    old_signature = file.read()
print(old_signature)

# compare hashes
if new_signature != old_signature:
    # overwrite existing bundle and hash
    with open(hash_path, 'w') as file:
        file.write(new_signature)
        shutil.move(bundle_path, (this_dir / '..' / 'dodcerts' / 'dod-ca-certs.pem').as_posix())
    print('update')
    exit(0)
else:
    exit(1)
