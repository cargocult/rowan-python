import os, sys

_id = None
def environment():
    """Returns the machine id that this install is running on."""
    global _id
    if _id is None:
        if 'ROWAN_MACHINE_ID' in os.environ:
            _id = os.environ['ROWAN_MACHINE_ID']
        else:
            try:
                file = '.machine_id'
                # try current working directory
                if os.path.isfile(file):
                    _id = open(file).read().strip()
                else:
                    # hunt in the sys.path
                    for d in sys.path:
                        filename = os.path.join(d, file)
                        if os.path.isfile(filename):
                            _id = open(filename).read().strip()
                            break
                    else:
                        raise IOError
            except IOError:
                _id = 'development'
                import textwrap
                print '\n'.join(textwrap.wrap(textwrap.dedent("""
                    Running as development server. If this is a
                    production machine, set the ROWAN_MACHINE_ID
                    environment variable (e.g. in the WSGI, shell
                    or mod_python configuration).  Alternatively
                    create a file called .machine_id containing an
                    id for your machine in the CWD or sys.path.
                    """), 76))
    return _id

def config(default=None, environment=environment(), **values):
    """Pick a specific configuration value for a specific environment."""
    if environment in values:
        return values[environment]
    else:
        return default
