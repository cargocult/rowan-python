# Standard preamble to add the rowan package to the Python path if it hasn't
# been installed yet (i.e. if we're just working in a checkout of the sourec
# tree).
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
from rowan.core.application import Application
from root import root
application = Application(root)

# A debugging server
if __name__ == '__main__':
    # Listen for all logging output
    import logging
    logging.basicConfig(level=logging.DEBUG)
    application.simple_serve()
