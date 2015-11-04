# Parselmouth


## What is Parselmouth?

Parselmouth serves as a facade/abstraction to adserver interfaces.
As of this writing (2015-11-03) Parselmouth only interfaces with Google's
Doubleclick for Publishers (DFP).

External API services like Google's DFP can be painful to interface with given
the irregularity of the data structures they use to communicate and the
frequency with which the API changes. Parselmouth aims to alleviate the pain of
using these services by standardizing a simple, pythonic object-oriented
interface that abstracts away the frustrating implementation details of an
external API.


## How do I get started?
#### Installing the library
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

#### Intializing Connection

Parselmouth can be initialized in one of the following ways:

##### Manually enumerating credentials:
```python
from parselmouth import Parselmouth
from parselmouth import ParselmouthProviders

client = Parselmouth(
    ParselmouthProviders.google_dfp_premium,  # Or google_dfp_small_business
    client_id='ID',
    client_secret='SECRET',
    refresh_token='REFRESH_TOKEN',
    network_code='NETWORK_CODE',
    application_name='APPLICATION_NAME',
)
```

##### Loading credentials from a configuration file:

Credentials may optionally be stored in a YAML file like the
[following](sample_config.yaml):
```yaml
google_dfp_premium:
    client_id: 'ID'
    client_secret: 'SECRET'
    refresh_token: 'REFRESH_TOKEN'
    network_code: 'NETWORK_CODE'
    application_name: 'APPLICATION_NAME'

google_dfp_small_business:
    client_id: 'ID'
    client_secret: 'SECRET'
    refresh_token: 'REFRESH_TOKEN'
    network_code: 'NETWORK_CODE'
    application_name: 'APPLICATION_NAME'
```

And then loaded like this:
```python
client = Parselmouth(
    provider_name=ParselmouthProviders.google_dfp_premium,
    config_path='sample_config.yaml',
)
```

##### Loading credentials from a configuration file:

Parselmouth may additionally be initialized using implementation-specific
configuration classes. These classes can be written to retrieve credentials from
external sources such as a SQL database or key-value store.

```python
from parselmouth import ParselmouthConfig  # Or your own custom config object

config = ParselmouthConfig(
    ParselmouthProviders.google_dfp_premium,
    config_path='sample_config.yaml',
)

client = Parselmouth(config)
```

##Basic Usage
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

For more details on working with delivery objects see [here](docs/delivery.md)

####Line Item Targeting

One of the most convenient features of Parselmouth is it's abstraction of
targeting information. Native API implementations of targeting configurations
are terribly complex, unwieldy, and difficult to manipulate. Parselmouth defines
a simple way of applying arbitrary boolean inclusion/exclusion criterion to a
LineItem.

```python
>>> from parselmouth.targeting import Geography
>>> usa = Geography(name='USA')
>>> canada = Geography(name='Canada')
>>> uk = Geography(name='UK')
>>> scotland = Geography(name='Scotland')
>>> na_region = TargetingCriterion([usa, canada], TargetingCriterion.OPERATOR.OR)
>>> uk_region = TargetingCriterion([uk, scotland], TargetingCriterion.OPERATOR.OR)
>>> target_either = na_region | uk_region
>>> target_na_only = na_region & ~uk_region
>>> target_neither = ~(na_region | uk_region)
```


For more details on targeting see [here](docs/targeting.md)

#### Trees

DFP also supports ad unit hierarchies governed by complex tree
structures.  For example a site might have an ad unit (or zone)
called Sports with child ad units called Sports/Hockey and
Sports/Baseball.  Both of these ad units share a parent ad unit
called Sports and are sibblings in this tree structure.
Parselmouth also supports functions which help in working with
these tree structures using objects called NodeTrees.

```python
>>> from parselmouth.constants import ParselmouthTargetTypes
>>> adunit_tree = client.construct_tree(ParselmouthTargetTypes.adunit)
>>> sports_tree = adunit_tree.get_subtree('name', 'Sports')
>>> for sub_unit in sports_tree.flatten():
...     print sub_unit.name
...
'Sports'
'Sports/Hockey'
'Sports/Baseball'
```

For more details on trees click [here](docs/trees.md)

####Object Serialization

All objects within Parselmouth can also be serialized to a dictionary.

```python
>>> line_item_doc = line_item.to_doc()
>>> print line_item_doc
{'status': 'COMPLETED', 'domain': None, 'targeting': {'video_position': None, 'day_part': None, 'custom': None, u'_metadata': {u'cls': 'TargetingData'}, 'inventory': {u'_metadata': {u'cls': 'TargetingCriterion'}, 'OR': [{'adunits': None, 'external_name': None, 'name': None, u'_metadata': {u'cls': 'Placement'}, 'parent_id': None, 'external_id': None, 'id': '1904883'}]}, 'video_content': None, 'user_domain': None, 'technology': None, 'geography': None}, 'name': 'Flight 1', 'cost_per_unit': {'budget_currency_code': 'USD', 'budget_micro_amount': 0.0, u'_metadata': {u'cls': 'Cost'}}, 'type': 'standard', 'campaign_id': '134419323', 'last_modified_by': 'Goog_DFPUI', 'value_cost_per_unit': {'budget_currency_code': 'USD', 'budget_micro_amount': 0.0, u'_metadata': {u'cls': 'Cost'}}, 'delivery': {'stats': {'video_completions': 0, u'_metadata': {u'cls': 'Stats'}, 'click_through_rate': 0, 'video_starts': 0, 'impressions': 572, 'clicks': 0}, 'pace': 5.72e-06, 'expected_delivery_percent': 100.0, u'_metadata': {u'cls': 'DeliveryMeta'}, 'delivery_rate_type': 'FRONTLOADED', 'actual_delivery_percent': 0.000572}, 'start': datetime.datetime(2013, 7, 31, 16, 30, tzinfo=<DstTzInfo 'America/New_York' LMT-1 day, 19:04:00 STD>), 'campaign_name': 'Test', 'cost_type': 'CPM', 'creative_placeholder': [{u'expectedCreativeCount': '1', u'creativeSizeType': 'PIXEL', u'size': {u'width': '300', u'isAspectRatio': False, u'height': '600'}}, {u'expectedCreativeCount': '1', u'creativeSizeType': 'PIXEL', u'size': {u'width': '728', u'isAspectRatio': False, u'height': '90'}}, {u'expectedCreativeCount': '1', u'creativeSizeType': 'PIXEL', u'size': {u'width': '300', u'isAspectRatio': False, u'height': '250'}}], u'_metadata': {u'cls': 'LineItem'}, 'last_modified': datetime.datetime(2013, 11, 20, 13, 34, 52, tzinfo=<DstTzInfo 'PST8PDT' PST-1 day, 16:00:00 STD>), 'budget': {'budget_currency_code': 'USD', 'budget_micro_amount': 0.0, u'_metadata': {u'cls': 'Cost'}}, 'primary_goal': {'unit_type': 'IMPRESSIONS', 'units': 100000000, 'goal_type': 'LIFETIME', u'_metadata': {u'cls': 'Goal'}}, 'end': datetime.datetime(2013, 9, 1, 23, 59, tzinfo=<DstTzInfo 'America/New_York' LMT-1 day, 19:04:00 STD>), 'target_platform': 'WEB', 'id': '74067003'}
```

And these dictionaries can be re-serialized back into their native type.

```python
>>> from parselmouth.delivery import LineItem
>>> reconstructed_line_item = LineItem.from_doc(line_item_doc)
>>> line_item == reconstructed_line_item
True
```

##Authors:
  * Justin Mazur: justin.mazur@chartbeat.com
  * Paul Kiernan: paul@chartbeat.com


## License: 

```
The MIT License (MIT)

Copyright (c) 2015 Chartbeat Labs Projects

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
