from setuptools import find_packages, setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='ini-parser',
    version='1.1.0',
    description='An ini parser/serializer in Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/YouTwitFace/ini-parser',
    author='Andrew Lane',
    author_email='contact@lungers.com',
    license='MIT',
    packages=find_packages()
)
