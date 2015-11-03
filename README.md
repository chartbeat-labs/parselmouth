#Parselmouth


## What is Parselmouth?

Parselmouth serves as a facade/abstraction to adserver interfaces. 
As of this writing (2015-11-03) Parselmouth only interfaces with Google's 
Doubleclick for Publishers (DFP).

Working with an external api service can be very painful for people, especially
ad service providers like DFP. The responses can have irregular data types and
structure, and are difficult to interface with. Parselmouth converts information
about advertising campaigns into pythonic object-oriented classes that are much
easier to use.


##How do I get started?
####Installing the library
Install or update the library from PyPI. If you're using pip, this is as easy
as:

`$ pip install [--upgrade] parselmouth`

If you don't want to install directly from PyPI, you can download the library
as a tarball and then install it manually. The download can be found here:
https://pypi.python.org/pypi/parselmouth
Navigate to the directory that contains your downloaded unzipped client
library and run the "setup.py" script to install the "parselmouth"
module.

`$ python setup.py build install`

####Intializing Connection

To connect to parselmouth using the DFP interface,
you input your credentials in the following way:

```python
from parselmouth import Parselmouth
from parselmouth import ParselmouthProviders

client = Parselmouth(
    ParselmouthProviders.google_dfp_premium,
    client_id='ID',
    client_secret='SECRET',
    refresh_token='REFRESH_TOKEN',
    network_code='NETWORK_CODE',
    application_name='APPLICATION_NAME',
)
```

You also have the option of storing this credential
information into a config file as seen in the
[sample config](sample_config.yaml).

```python
client = Parselmouth(
    provider_name=ParselmouthProviders.google_dfp_premium,
    config_path='sample_config.yaml',
)
```

You may also manually initialize your config using
the native configuration class:

```python
from parselmouth import ParselmouthConfig

config = ParselmouthConfig(
    ParselmouthProviders.google_dfp_premium,
    config_path='sample_config.yaml',
)

client = Parselmouth(config)
```

##Basic Usage
Detailed usage of each function on Parselmouth can be
found [here]

####Campaigns
A primary use-case of Parselmouth is to obtain information
about ad campaigns from an ad service provider.

```python
>>> campaign = client.get_campaign('ORDER_ID')
>>> campaign.id
'ORDER_ID'
>>> campaign.name
'ORDER_NAME'
>>> campaign.start
datetime.datetime(2013, 7, 31, 16, 30, tzinfo=<DstTzInfo 'America/New_York' LMT-1 day, 19:04:00 STD>)
>>> campaign.stats
Stats({'video_completions': 0, 'impressions': 572, 'click_through_rate': 0, 'clicks': 0, 'video_starts': 0})
```

####Line Items and Creatives
You can also get line item and creative objects
```python
>>> line_items = client.get_campaign_line_items(campaign)
>>> line_item = line_items[0]
>>> line_item.id
'LINE_ITEM_ID'
>>> creatives = client.get_line_item_creatives(line_item)
>>> creatives[0].id
'CREATIVE_ID'
```

####Line Item Targeting

Another important feature, is the ease in which you can manage
and manipulate line item targeting information.  Targeting is
notoriously difficult to work with because of its complexity.
This is due to the fact that targeting can be customly configured
and can have arbitrary boolean structure.  Different types of
targeting are housed in the TargetingCriterion class.

```python
>>> targeting = line_item.targeting
>>> print targeting
TargetingData({'video_position': None, 'day_part': None, 'custom': None, 'inventory': TargetingCriterion({'OR': [Placement({'adunits': None, 'external_name': None, 'name': None, 'parent_id': None, 'external_id': None, 'id': 'ID'})]}), 'video_content': None, 'user_domain': None, 'technology': None, 'geography': None})
>>> print targeting.inventory
```

For more details on targeting see [here]

#### Trees

Trees suck.



##Authors:
  Justin Mazur: justin.mazur@chartbeat.com
  Paul Kiernan: paul@chartbeat.com
