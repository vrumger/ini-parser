import re

from setuptools import find_packages, setup

with open('README.md') as f:
    long_description = f.read()

with open('ini/__init__.py', 'r', encoding='utf-8') as f:
    version = re.search(r"^__version__ = '(.*?)'$", f.read(), flags=re.MULTILINE).group(1)

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
    packages=find_packages()
)
