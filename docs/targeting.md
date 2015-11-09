#Line Item Targeting

Targeting is very important to advertising campaigns.
However, since targeting can apply to almost anything
you can think with any inclusionary or exclusionary rules,
managing targeting within a line item can become very complicated.
Parselmouth currently supports the following types of targeting:

####Inventory

Inventory targeting involves targeting AdUnits, which
represent either a zone or an ad position on a site,
or Placements, which represent a custom set of AdUnits.

The inventory targeting for a LineItem object can be
obtained in the following way:

```python
inventory = line_item.targeting.inventory
```

####Geography

Geography targeting involves targeting specific geographical
regions such as cities, countries, or regions.

The geography targeting for a LineItem object can be
obtained in the following way:

```python
geography = line_item.targeting.geography
```

####Technology

Technology targeting involves targeting specific technologies
types such as specific browsers, devices, platforms,
and operating systems.

The technology targeting for a LineItem object can be
obtained in the following way:

```python
technology = line_item.targeting.technology
```

####Custom

Custom targeting information that is configured on a per website
basis.  This can include demograpic data or any kind of information
that might be relevant to a particular sites users or data.

The custom targeting for a LineItem object can be
obtained in the following way:

```python
custom = line_item.targeting.custom
```


##TargetingCriterion

All of the above examples are instance of the TargetingCriterion
class.  This is a class that allows for aribitrary boolean structure
so that one can target or exclude any combination of targets.

For example, if you want to target specific geographic regions you
could create the following TargetingCriterion:

```python
from parselmouth.targeting import Geography

# Initialize some geography targets
usa = Geography(name='USA')
canada = Geography(name='Canada')
uk = Geography(name='UK')
scotland = Geography(name='Scotland')

# Initialize some regional TargetingCriterion
na_region = TargetingCriterion([usa, canada], TargetingCriterion.OPERATOR.OR)
uk_region = TargetingCriterion([uk, scotland], TargetingCriterion.OPERATOR.OR)

# Build new TargetingCriterion using boolean operators
target_either = na_region | uk_region
target_na_only = na_region & ~uk_region
target_neither = ~(na_region | uk_region)
```


## Updating a LineItem Targeting

Consider the case where you have a LineItem object with a predefined set
of targets.  Lets walk through how you might add female demographic
targeting to this line item.

First you need to locate the custom targeting information associated
with the female demograpic from the ad provider.
Note: Since this is custom targeting information, you would have to
look up the correct lookup names associated to a female demo target
for the account you are using.  By the very nature of custom targeting,
it can vary from account to account.

```python
female_demo = client.get_custom_target_by_name(
    name='Female',
    parent_name='gender',
)
```

Create a new custom target that requires that only females
see creatives associated with this line item.  Then, update
the line item on the ad providers end.

```python
old_custom = line_item.targeting.custom

# Create targeting criterion for female demo target
female_target = TargetingCriterion(female_demo)

# Apply female demo target to previous custom target
new_custom = old_custom & female_target

# Update custom targeting
line_item.targeting.custom = new_custom

# Send updated information to ad provider
client.update_line_item(line_item)
```
