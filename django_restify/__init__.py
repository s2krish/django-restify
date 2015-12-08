from importlib import import_module


def import_attr(package_path):
    """Returns the callable from string package path e.g. """
    """in mymodule.views.myview, it loads myview callable"""

    mod_path, _, attr = package_path.rpartition('.')
    module = import_module(mod_path)
    attr = getattr(module, attr)

    return attr

VERSION = '0.1.9'
