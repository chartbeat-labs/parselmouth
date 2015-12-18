from setuptools import setup, find_packages

setup(
    name='parselmouth',
    packages=find_packages(),
    version='1.1.1',
    description=(
        'An object oriented interface for ad provider services in python'
    ),
    author='Paul Kiernan, Justin Mazur',
    author_email='paulkiernan1@gmail.com, justindmazur@gmail.com',
    url='https://github.com/chartbeat-labs/parselmouth',
    download_url='https://github.com/chartbeat-labs/parselmouth/tarball/1.1.1',
    keywords = ['googleads', 'dfp', 'ad server', 'parselmouth', 'ad provider'],
    classifiers = [],
    install_requires=[
        'googleads==3.8.0',
        'pytz==2015.7',
        'stopit==1.1.1',
    ],
)
