#Parseltounge Third Party Adapters

## What is a Parseltounge Adapter?

Parseltounge is an abstraction to external ad server APIs. This submodule
contains the implementers required by the
["bridge" programming pattern](http://en.wikipedia.org/wiki/Bridge_pattern).

Adapters fit into the following class diagram:
![Bridge Class Diagram](assets/Bridge_UML_class_diagram.png)

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

### [Google Doubleclick for Publishers](https://developers.google.com/doubleclick-publishers/docs/start)

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
