from setuptools import setup, find_packages

setup(
    name='vm_interactor',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'paramiko',
        'python-dotenv',
    ],
)