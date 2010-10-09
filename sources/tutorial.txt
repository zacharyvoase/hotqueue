========
Tutorial
========

A HotQueue is a simple FIFO queue that maps to a list key in Redis. The following is a brief introduction explaining how you can use HotQueue in practice with a simple example. 

Connecting to Redis
===================

Creating a queue is as simple as creating a :class:`~hotqueue.HotQueue` instance:

    >>> from hotqueue import HotQueue
    >>> queue = HotQueue('myqueue', host='localhost', port=6379, db=0)

The queue will be stored a Redis list key named ``hotqueue:myqueue``, on the Redis server running at ``localhost:6379``, in database ``0``. The :attr:`host`, :attr:`port` and :attr:`db` arguments are optional.

Putting Items Onto the Queue
============================

Then you may have one (or many) Python programs pushing to the queue using :meth:`hotqueue.HotQueue.put`:

    >>> queue.put(4)
    >>> queue.put(5)

You can push more than one item onto the queue at once:

    >>> queue.put(6, 'my message', 7)

You can safely push **any Python object** that can be `pickled <http://docs.python.org/library/pickle.html>`_. Let's use Python's built-in ``Decimal`` as an example:

    >>> from decimal import Decimal
    >>> queue.put(Decimal('1.4'))

Getting Items Off the Queue
===========================

You can then pull items off the queue using :meth:`hotqueue.HotQueue.get`. You would usually do this in another Python program, but you can do it wherever you like.

    >>> queue.get()
    4
    >>> queue.get()
    5
    >>> queue.get()
    6
    >>> queue.get()
    'my message'
    >>> queue.get()
    7
    >>> dec = queue.get()
    >>> dec
    Decimal('1.4')
    >>> dec + Decimal('0.3')
    Decimal('1.7')

Consuming the Queue
===================

A better way to pull items off the queue is to use :meth:`hotqueue.HotQueue.consume`, which returns a generator that yields whenever an item is on the queue and blocks otherwise. Here's an example:

    >>> for item in queue.consume():
    ...     print item

If you push to the queue using :meth:`hotqueue.HotQueue.put` in another Python program, you will see this program print the message then wait indefinitely for another. Replace the ``print`` statement with something more interesting, like saving a record to a database, and you've created an asynchronous task.

Writing a Queue Worker
======================

An `even better` way to pull items off the queue is to use the :meth:`hotqueue.HotQueue.worker` decorator. Using this decorator is like wrapping the decorated function in a :meth:`hotqueue.HotQueue.consume` loop. Here's an example::

    from hotqueue import HotQueue
    
    queue = HotQueue('myqueue', host='localhost', port=6379, db=0)
    
    @queue.worker
    def square(num):
        print num * num

Then run the function:

    >>> square()

It will wait indefinitely and print the square of any integers it pulls off the queue. Try pushing some integers to the queue in another Python program:

    >>> queue.put(2, 3, 4)

To distribute the work, run a second instance of ``square()``. You now have two queue workers. You can run as many workers as you like, and no two workers will ever receive the same message.

To run and manage your worker processes, you could use something like `Supervisord <http://supervisord.org/>`_.
