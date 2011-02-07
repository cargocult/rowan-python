#!/usr/bin/env python

# Standard preamble to add the rowan package to the Python path if it
# hasn't been installed yet (i.e. if we're just working with an
# example in a checkout of the source tree).
if __name__ == '__main__':
    try:
        import rowan
    except ImportError:
        import sys
        import os
        sys.path.append(os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..',  '..')
            ))

# Content for this example.
from rowan.application import Application
from root import root
application = Application(root)

def main():
    # Listen for the correct level of logging output
    import logging
    logging.basicConfig(level=logging.WARNING)
    application.simple_serve()

# A debugging server
if __name__ == '__main__':
    from rowan.utils import autoreload
    autoreload.main(main)
