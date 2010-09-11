===========================
HotQueue User Documentation
===========================

HotQueue is a Python library that allows you to use `Redis <http://code.google.com/p/redis/>`_ as a message queue within your Python programs.

The main advantage of this model is that there is no queue server to run, other than Redis. This is particularly ideal if you're already using Redis as a datastore elsewhere. To install it, run:

.. code-block:: console

    # easy_install -U hotqueue

The source code is available on `GitHub <http://github.com/richardhenry/hotqueue>`_.

To get help with HotQueue, use the `HotQueue Users mailing list
<http://groups.google.com/group/hotqueue-users>`_.

Introduction
============

A HotQueue is a simple FIFO queue that maps to a list key in Redis. Creating a queue is as simple as creating a :class:`~hotqueue.HotQueue` instance:

    >>> from hotqueue import HotQueue
    >>> queue = HotQueue('myqueue', host='localhost', port=6379, db=0)

You can then push messages onto this queue using the :meth:`~hotqueue.HotQueue.enqueue` method:

    >>> queue.enqueue('my message')
    >>> queue.enqueue('another message')

To pull messages off the queue, use :meth:`~hotqueue.HotQueue.dequeue`. If the queue is empty, the :meth:`~hotqueue.HotQueue.dequeue` method will return ``None``. Here's how:

    >>> queue.dequeue()
    'my message'
    >>> queue.dequeue()
    'another message'

Messages don't have to be strings, you can enqueue any Python object. HotQueue will handle object serialization and deserialization for you using `pickle <http://docs.python.org/library/pickle.html>`_. This can be useful, as it allows you to share Python objects between programs. Here's an example:

    >>> queue.enqueue({'cat': 'meow', 'dog': 'woof'})
    >>> sounds = queue.dequeue()
    >>> sounds['cat']
    'meow'
    >>> sounds['dog']
    'woof'
    >>> class MyClass(object):
    ...     weather = 'rainy'
    >>> queue.enqueue(MyClass())
    >>> my_class = queue.dequeue()
    >>> print my_class.weather
    rainy

In most cases, you will want to use the :meth:`~hotqueue.HotQueue.consume` method when writing a queue worker. This method will return a generator that yields whenever an item is available on the queue, and will block otherwise. Use this method like so:

    >>> queue.enqueue('blue', 'green', 'red', 'white')
    >>> for item in queue.consume():
    ...     print item
    blue
    green
    red
    white

If you want the worker to "give up" if nothing is in the queue for a certain amount of time, you can provide a :attr:`timeout` value in seconds:

.. code-block:: python

    queue.consume(timeout=5)

It is perfectly safe to have many workers consuming from the same queue. This method makes use of the ``BLPOP`` command available in Redis, and `documented here <http://code.google.com/p/redis/wiki/BlpopCommand>`_.

Further Reading
===============

.. toctree::
   :maxdepth: 2
   
   apireference
   changelog

Requirements
============

HotQueue requires, at a minimum:

- `Redis <http://code.google.com/p/redis/>`_ version 1.3.1+
- `redis-py <http://pypi.python.org/pypi/redis/2.0.0>`_ version 2.0.0+