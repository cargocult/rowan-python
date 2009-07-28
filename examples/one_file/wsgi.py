if __name__ == '__main__':
    import sys; sys.path.append('.')

from rowan.core.application import Application
import controller
application = Application(controller.root)

# A debugging server
if __name__ == '__main__':
    # Listen for all logging output
    import logging
    logging.basicConfig(level=logging.INFO)
    application.simple_serve()
