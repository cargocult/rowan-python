if __name__ == '__main__':
    import sys; sys.path.append('.')

from rowan.core.application import Application
from root import root
application = Application(root)

# A debugging server
if __name__ == '__main__':
    # Listen for all logging output
    import logging
    logging.basicConfig(level=logging.DEBUG)
    application.simple_serve()
