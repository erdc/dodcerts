from setuptools import setup, find_packages
import versioneer

requirements = [
    'cryptography',
]

entry_points = [
    'dodcerts = dodcerts.cli:cli',
]

setup(
    name='dodcerts',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="DoD Certificate Chain",
    author="Kevin Winters",
    author_email='Kevin.D.Winters@erdc.dren.mil',
    url='https://github.com/erdc/dodcerts',
    license='BSD',
    packages=['dodcerts'],
    package_data={'dodcerts': ['dod-ca-certs.pem'],},
    entry_points={'console_scripts': entry_points,},
    install_requires=requirements,
    keywords='dodcerts',
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable',
    ]
)
