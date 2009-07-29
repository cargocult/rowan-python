from __future__ import with_statement
import contextlib

class Blackboard(object):
    """A data store who's value updates are reversable.
    
    This is intended to be used on its own, and as a base class of various 
    other data storage classes, such as the HttpRequest object passed
    to controllers.
        
    >>> b = Blackboard()
    >>> with b.set(foo=2): 
    ...     print b.foo
    2
    >>> print b.foo
    Traceback (most recent call last):
        ...
    AttributeError: 'Blackboard' object has no attribute 'foo'
    >>> with b.set(foo__bar=2):
    ...     print b.foo.__class__.__name__
    ...     print type(b.foo.bar)
    ...     print b.foo.bar
    Blackboard
    <type 'int'>
    2
    """

    @contextlib.contextmanager
    def set(self, **kws):
        """
        A context for temporarily setting values in the request.
        
        Use this method as part of a with statement to make sure
        that any changes you make to the request are limited to the nodes
        further down the tree. The keyword arguments for this method
        are the settings you want to change. Keywords can be given in
        ``a__b`` format, where the ``__`` indicates nesting. So ``a__b=2`` 
        finds the ``a`` property of this blackboard and looks in that object 
        for a property called ``b``, which it sets to 2. These nested objects
        don't need to be blackboards, the blackboard will manage any
        kind of object at that point.
        
        If a setting isn't already present, it will be created by
        this blackboard, intermediate objects given with nested keys
        will be created as empty blackboards, if they don't already exist.
        """
        # Make the changes, storing the old versions for future use.
        old_values = {}
        new_values = []
        for key, value in kws.items():
            # Work out the nesting of this parameter
            components = key.split('__')
            
            # Go through the components and see if they exist
            obj = self
            found_new = False
            for component in components[:-1]:
                if hasattr(obj, component):
                    obj = getattr(obj, component)
                else:
                    if not found_new:
                        # This is the first new item we're creating,
                        # so add it to the new list.
                        new_values.append((obj, component))
                        found_new = True
                        
                    # Set the blackboard in the given slot and recurse into it.
                    blackboard = Blackboard()
                    setattr(obj, component, blackboard)
                    obj = blackboard
                    
            # The final stage should be the value, not a blackboard.
            last_component = components[-1]
            if hasattr(obj, last_component):
                old_values[(obj, last_component)]=getattr(obj, last_component)
            elif not found_new:
                new_values.append((obj, last_component))
            setattr(obj, last_component, value)
            
        # Yield back to the context.
        try:
            yield
            
        # Reset everything back to how it was.
        finally:
            for (obj, key), value in old_values.items():
                setattr(obj, key, value)
            for (obj, key) in reversed(new_values):
                delattr(obj, key)
                
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    