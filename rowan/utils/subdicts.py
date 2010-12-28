class ChangeTrackingDict(dict):
    """
    A dictionary subclass that has a field for tracking if the
    dictionary is dirty and needs saving.
    """
    def __init__(self, *args, **kws):
        super(ChangeTrackingDict, self).__init__(*args, **kws)
        self.dirty = False

    def __setitem__(self, key, value):
        """
        Sets a value associated with a key, automatically updating the
        record of whether this dictionary is dirty.
        """
        if self.dirty:
            # Quick version if we're already dirty.
            super(ChangeTrackingDict, self).__setitem__(key, value)
        else:
            old_value = self[key]
            super(ChangeTrackingDict, self).__setitem__(key, value)
            self.dirty = (old_value != value)

    def clean(self):
        """
        Notifies this dictionary that its data should be clean
        (i.e. saved).
        """
        self.dirty = False

class MultipleSourceDict(object):
    """
    A dictionary-like object that delegates to a number of other
    dictionaries.
    """
    def __init__(self, *others):
        self.others = others

    def __setitem__(self, key, value):
        for other in self.others:
            if key in other:
                other[key] = value
                break
        else:
            raise KeyError("Key not found in delegates: %s" % key)

    def __getitem__(self, key):
        for other in self.others:
            if key in other:
                return other[key]
        raise KeyError("Key not found in delegates: %s" % key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __delitem__(self, key):
        for other in self.others:
            if key in other:
                del other[key]
                break
        else:
            raise KeyError("Key not found in delegates: %s" % key)

    def __in__(self, key):
        for other in self.others:
            if key in other:
                return True
        else:
            return False
