from setuptools import setup

setup(
    name='parselmouth',
    packages=['parselmouth'],
    version='0.1',
    description=(
        'An object oriented interface for ad provider services in python'
    ),
    author='Paul Kiernan, Justin Mazur',
    author_email='paulkiernan1@gmail.com, justindmazur@gmail.com',
    url='https://github.com/chartbeat-labs/parselmouth',
    download_url = 'https://github.com/chartbeat-labs/parselmouth/tarball/0.1',
    keywords = ['googleads', 'dfp', 'ad server', 'parselmouth', 'ad provider'],
    classifiers = [],
    install_requires=[
        'googleads==3.8.0',
        'pytz==2015.7',
        'python-cjson==1.1.0',
    ],
)
