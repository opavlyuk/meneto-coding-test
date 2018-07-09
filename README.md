TEST PROJECT FOR MENETO
====================

Tested under GNU/Linux system.
API needs extending, but it would take a bit more time.
Hope, project consists enough code to make decision about my skills.

REQUIREMENTS
------------

Python >= 3.6


GET SOURCE
----------

Clone the project and open work directory.

```
$ git clone https://github.com/opavlyuk/meneto-coding-test.git
$ cd meneto-coding-test

```

INSTALL
-------

1. Make python3 virtualenv and activate it:

```
$ python3 -m venv venv && source venv/bin/activate

```

2. Install required packages into virtualenv:

```
(venv) $ pip install -r requirements.txt

```

RUN
-------

**Please consider running tests rather then run.py script**

1. Ensure that run.py is executable:

```
(venv) $ chmod +x run.py

```

2. Execute run script:

```
(venv) $ /.run.py

```

TEST
----

Execute unit tests:

```
(venv) $ python -m unittest

```

Note: Traceback KeyError: 'Product with id 3 not found' **IS** expected
