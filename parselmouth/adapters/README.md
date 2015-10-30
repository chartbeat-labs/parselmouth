#Parseltounge Third Party Adapters

![adapter](../../assets/adapter.jpg)

**Maintainers:**

* Justin Mazur: justin.mazur@chartbeat.com
* Paul Kiernan: paul@chartbeat.com


## What is a Parseltounge Adapter?

Parseltounge is an abstraction to external ad server APIs. This submodule
contains the implementers required by the
["bridge" programming pattern](http://en.wikipedia.org/wiki/Bridge_pattern).

Adapters fit into the following class diagram:
![Bridge Class Diagram](../../assets/Bridge_UML_class_diagram.png)

* **Abstraction (abstract class)**
    * Defines the abstract interface to an ad service.
    * Maintains the implementor reference for a specific ad service.
    * Think of this as the proxy to all interfaces. It defines common models and
      methods and is coupled with a specific implementation at instantiation.
* **RefinedAbstraction (normal class)**
    * Extends the interface defined by the abstraction
    * Instantiates the chartbeat ad service abstraction with a specific client's
      implementation.
    * Additionally includes chartbeat functionality separate from ad services
* **Implementor (interface)**
    * Defines the interface for the implementation classes
    * This is the bridge between an ad service's native client library and
      chartbeat's abstraction.
* **Concrete Implementor (normal class)**
    * Implements the implementor interface
    * This is an ad services native client library


## Currently Supported Ad Services (2015-02-25)

### [Google Doubleclick for Publishers](dfp/README.md)
