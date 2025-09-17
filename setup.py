import re

from setuptools import find_packages
from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

with open('ini/__init__.py', encoding='utf-8') as f:
    match = re.search(r"^__version__ = '(.*?)'$", f.read(), flags=re.MULTILINE)
    if not match:
        raise Exception('cannot find version')
    version = match.group(1)


setup(
    name='ini-parser',
    version=version,
    description='An ini parser/serializer in Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/vrumger/ini-parser',
    author='Avrumy Lunger',
    author_email='contact@lungers.com',
    license='MIT',
    packages=find_packages(),
)
