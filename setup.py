from setuptools import setup, find_packages

setup(
    name='parseltongue',
    version='2.7',
    packages=find_packages(),
    install_requires=[
        'googleads==3.8.0',
        'pytz==2015.7',
    ],
)
