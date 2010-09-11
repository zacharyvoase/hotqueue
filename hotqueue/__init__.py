# -*- coding: utf-8 -*-

import cPickle

from redis import Redis


__all__ = ['HotQueue']

__version__ = '0.1'


class HotQueue(object):
    
    """Simple FIFO message queue stored in a Redis list.
    
    :param name: name of the queue
    :param kwargs: additional kwargs to pass to :class:`Redis`, most commonly
        :attr:`host`, :attr:`port`, :attr:`db`
    """
    
    def __init__(self, name, **kwargs):
        """
        >>> queue = HotQueue('doctestq', host='localhost', port=6379, db=0)
        >>> queue.clear()
        >>> queue.enqueue('my message')
        >>> len(queue)
        1
        >>> queue.enqueue('another message')
        >>> len(queue)
        2
        >>> queue.dequeue()
        'my message'
        >>> queue.dequeue()
        'another message'
        >>> queue.clear()
        >>> queue.enqueue('dog')
        >>> len(queue)
        1
        >>> queue.enqueue('rabbit', 'mouse')
        >>> len(queue)
        3
        >>> for item in queue.consume(timeout=1):
        ...     print item
        dog
        rabbit
        mouse
        >>> queue.enqueue('Richard', 'Michael', 'Henry')
        >>> len(queue)
        3
        >>> queue.dequeue(block=True)
        'Richard'
        >>> len(queue)
        2
        >>> queue.dequeue(block=True, timeout=1)
        'Michael'
        >>> len(queue)
        1
        >>> for item in queue.consume(block=False):
        ...     print item
        Henry
        >>> len(queue)
        0
        >>> queue.enqueue({'cat': 'meow', 'dog': 'woof', 'cow': 'moo'})
        >>> sounds = queue.dequeue()
        >>> sounds['cat'] == 'meow'
        True
        >>> sounds['dog'] == 'woof'
        True
        >>> sounds['cow'] == 'moo'
        True
        >>> queue.clear()
        """
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
                message = self.dequeue(block=block, timeout=timeout)
                if message is None:
                    break
                yield message
        except KeyboardInterrupt:
            print; return
    
    def dequeue(self, block=False, timeout=None):
        """Return a message from the queue.
        
        :param block: whether or not to wait until a message is available in
            the queue before returning; ``False`` by default
        :param timeout: when using :attr:`block`, if no message is available
            for :attr:`timeout` in seconds, return ``None``
        """
        if timeout is None:
            timeout = 0
        if block:
            message = self.__redis.blpop(self.key, timeout=timeout)
            if message is not None:
                message = message[1]
        else:
            message = self.__redis.lpop(self.key)
        if message is not None:
            message = cPickle.loads(message)
        return message
    
    def enqueue(self, *messages):
        """Push one or more messages onto the queue."""
        for message in messages:
            message = cPickle.dumps(message)
            self.__redis.rpush(self.key, message)

