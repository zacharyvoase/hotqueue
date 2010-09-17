# -*- coding: utf-8 -*-

"""HotQueue is a Python library that allows you to use Redis as a message queue
within your Python programs.
"""

from functools import wraps
import cPickle

from redis import Redis


__all__ = ['HotQueue']

__version__ = '0.2.0'


class HotQueue(object):
    
    """Simple FIFO message queue stored in a Redis list.
    
    :param name: name of the queue
    :param kwargs: additional kwargs to pass to :class:`Redis`, most commonly
        :attr:`host`, :attr:`port`, :attr:`db`
    """
    
    def __init__(self, name, **kwargs):
        self.name = name
        self.__redis = Redis(**kwargs)
    
    def __len__(self):
        return self.__redis.llen(self.key)
    
    def __repr__(self):
        return ('<HotQueue: \'%s\', host=\'%s\', port=%d, db=%d>' %
            (self.name, self.__redis.host, self.__redis.port, self.__redis.db))
    
    @property
    def key(self):
        """Return the key name used to store this queue in Redis, determined
        from :attr:`name`. Usually like ``hotqueue:name``.
        """
        return 'hotqueue:%s' % self.name
    
    def clear(self):
        """Clear the queue of all messages, deleting the Redis key."""
        self.__redis.delete(self.key)
    
    def consume(self, block=True, timeout=None):
        """Return a generator that yields whenever a message is waiting in the
        queue. Will block otherwise.
        
        :param block: whether or not to wait until a message is available in
            the queue before yielding; ``True`` by default
        :param timeout: when using :attr:`block`, if no message is available
            for :attr:`timeout` in seconds, return ``None``
        """
        try:
            while True:
                msg = self.get(block=block, timeout=timeout)
                if msg is None:
                    break
                yield msg
        except KeyboardInterrupt:
            print; return
    
    def get(self, block=False, timeout=None):
        """Return a message from the queue.
        
        :param block: whether or not to wait until a msg is available in
            the queue before returning; ``False`` by default
        :param timeout: when using :attr:`block`, if no msg is available
            for :attr:`timeout` in seconds, return ``None``
        """
        if block:
            if timeout is None:
                timeout = 0
            msg = self.__redis.blpop(self.key, timeout=timeout)
            if msg is not None:
                msg = msg[1]
        else:
            msg = self.__redis.lpop(self.key)
        if msg is not None:
            msg = cPickle.loads(msg)
        return msg
    
    def put(self, *msgs):
        """Push one or more messages onto the queue.
        
        :param msgs: one or more messages to push onto the queue
        """
        for msg in msgs:
            msg = cPickle.dumps(msg)
            self.__redis.rpush(self.key, msg)
    
    def worker(self, **kwargs):
        """Decorator for using a function as a queue worker.
        
        :param kwargs: any arguments that :meth:`~hotqueue.HotQueue.consume`
            can accept (such as :attr:`timeout`)
        """
        def decorator(worker):
            @wraps(worker)
            def wrapper():
                for msg in self.consume(**kwargs):
                    worker(msg)
            return wrapper
        return decorator

