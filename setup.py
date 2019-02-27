from setuptools import setup, find_packages
import versioneer

requirements = [
    'cryptography',
]

setup(
    name='dodcerts',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="DoD Certificate Chain",
    author="Kevin Winters",
    author_email='Kevin.D.Winters@erdc.dren.mil',
    url='https://github.com/erdc/dodcerts',
    packages=['dodcerts'],
    package_data={'dodcerts': ['dod-ca-certs.pem',],},
    entry_points={},
    install_requires=requirements,
    keywords='dodcerts',
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ]
)
