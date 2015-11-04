# Delivery Objects

Here is a list of all delivery objects that are currently available in
Parselmouth.

## Campaign

A campaign (or order) typically represents a deal between and advertiser and an
online content provider. This object holds high level information about an
advertising campaign such as the advertiser, a date range, status, and budget.

#### Usage

If you know the ID of a given campaign you can get a Campaign
object in the following way:

```python
campaign = client.get_campaign('ORDER_ID')
campaign = client.get_campaigns(id='ORDER_ID')
campaigns = client.get_campaigns(id=['ORDER_ID1', 'ORDER_ID2'])
all_campaigns = client.get_campaigns()
```

You also have the ability to query for a larger group of campaigns

## LineItem

A LineItem describes the set of requirements for an ad to show on a domain. It
includes how and when a line item should be shown, the sizes of the creatives to
show, the priority of these ads, and several properties related to the cost of
the ads. It also describes particular AdUnits, Placements, Geographies, and etc.
other targeting criterion to which impressions should be delivered.

Parselmouth facilitates the retrieval and updating of a LineItem through the
following calls, respectively:
* `Parselmouth.get_line_item` _or_ `Parselmouth.get_line_items`
* `Parselmouth.update_line_items`

#### Usage

##### Fetching LineItem(s)

```python
# Fetching a single line item
line_item = parselmouth_client.get_line_item("id1")

# Or like this:
line_item = parselmouth_client.get_line_items(id="id1")

# Fetching multiple line items by id
line_item_ids = ["id1", "id2", ... , "idN"]
line_items = parselmouth_client.get_line_items(id=line_item_ids)

# Fetching all line items
# NOTE: This can be very slow
all_line_items = client.get_line_items()
```

##### Updating a Line Item

Line Item objects contain three immutable properties that encode its identity
and therefore cannot be changed:
    * Id
    * Type
    * Start Date

So to update a line item we simply take an existing one, change any of its
properties (excluding the three listed above) and submit the line item to the
update API like this:

```python
# Given a LineItem `line_item`, swap out some cust target
original_custom_target = line_item.targeting.custom
new_custom_target = get_custom_target(FOO)
new_line_item = deepcopy(line_item)
new_line_item.targeting.custom = new_custom_target
parselmouth_client.update_line_item(new_line_item)
```

###### Checking for available inventory before updating a line item

Oftentimes when updating line item delivery requirements on a popular domain
there may not be enough available inventory to contribute. DFP will
automatically make this check when submitting updates to a line item, however,
it is possible to make these checks manually if that is desired:

```python
available_impressions = parselmouth_client.get_line_item_available_inventory(
    updated_line_item,
    use_start=True,
    preserve_id=True
)
```

The `use_start` and `preserve_id` parameters to this function are required when
updating a line item in order to get an accurate report on the adjusted
available inventory. `preserve_id` is not required when checking for available
inventory for a new LineItem and `use_start` is only required for a new LineItem
when the start date is in the future.

#### Line Item Reports

Parselmouth provides the ability to report on the status of all line items over
a given time period:

```python
start = datetime(2014, 1, 1)
end = datetime.today()
line_item_report = parselmouth_client.get_line_item_report(start, end)
```

## Creative

A creative represents an actual ad that would be served up by a booked LineItem.

#### Usage

```python
creative = parselmouth_client.get_creative("creative_id")
creative = parselmouth_client.get_creatives(id="creative_id")
creatives = parselmouth_client.get_creative(id=["creative_id1", "creative_id2"])
```

### Secondary Objects

#### Cost

Basic container for modeling Campaign and Line Item Budgets and Costs.

#### Goal

Basic container for modeling Campaign delivery goals.

#### Stats

Basic container for tracking an item's delivery performance like the number of
impressions served.

#### DeliveryMeta

Basic container for tracking delivery expectations like the actual delivery
percent for a campaign and the expected delivery percent.
