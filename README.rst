===============================
dodcerts
===============================

.. image:: https://travis-ci.com/erdc/dodcerts.svg?branch=master
.. image:: https://ci.appveyor.com/api/projects/status/058qfkppjlbgxqjh/branch/master?svg=true
.. image:: https://codecov.io/gh/erdc/dodcerts/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/erdc/dodcerts

DoD Certificate chain

dodcerts is a simple Certificate Authority (CA) certificate Python package providing U.S. Government DoD root and intermediate certificates as a PEM bundle.

When installed, this package includes **dod-ca-certs.pem** and methods to locate it:

* Command line interface (CLI): ::

    $ dodcerts

    '/Users/kajiglet/Library/Caches/Python-Eggs/dodcerts-1.0-py3.6.egg/dodcerts/dod-ca-certs.pem'

* Python: ::

    >>> import dodcerts
    >>> dodcerts.where()
    '/Users/kajiglet/Library/Caches/Python-Eggs/dodcerts-1.0-py3.6.egg/dodcerts/dod-ca-certs.pem'

The path to the PEM bundle returned by the above methods may be overloaded by setting the value of the ``DOD_CA_CERTS_PEM_PATH`` environment variable.

dodcerts also provides a method to create a new PEM bundle based on provided certificates by specifying URLs to resources or pointing at a local directory containing the certs. This method can set ``DOD_CA_CERTS_PEM_PATH`` to easily reference the result (only valid within the calling Python process and its child processes): ::

  >>> import os, dodcerts
  >>> os.getenv('DOD_CA_CERTS_PEM_PATH')
  >>> dodcerts.where()
  '/Users/kajiglet/Library/Caches/Python-Eggs/dodcerts-1.0-py3.6.egg/dodcerts/dod-ca-certs.pem'
  >>> from dodcerts.create import create_pem_bundle
  >>> create_pem_bundle(destination='./my_bundle.pem', urls='https://militarycac.org/maccerts/AllCerts.zip', set_env_var=True)
  '/Users/kajiglet/test/my_bundle.pem'
  >>> os.getenv('DOD_CA_CERTS_PEM_PATH')
  '/Users/kajiglet/test/my_bundle.pem'
  >>> dodcerts.where()
  '/Users/kajiglet/test/my_bundle.pem'