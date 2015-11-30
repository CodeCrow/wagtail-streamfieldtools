import copy
from collections import OrderedDict

from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule

from wagtail.wagtailcore.blocks import Block


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class InvalidBlock(Exception):
    pass


class RegisteredBlockStreamFieldRegistry(object):
    """
    Allows instances of wagtail.wagtailcore.blocks.Block to be registered with
    RegisteredBlockStreamField on an app-by-app basis.
    """

    def __init__(self):
        self._registry = OrderedDict()

    def _verify_block(self, attr_name, block):
        """
        Verifies a block prior to registration.
        """
        if attr_name in self._registry:
            raise AlreadyRegistered(
                "A block has already been registered to the {} `attr_name` in "
                "the registry. Either unregister that block before trying to "
                "register this block under a different `attr_name`".format(
                    attr_name
                )
            )
        if not isinstance(block, Block):
            raise InvalidBlock(
                "The block you tried register to {} is invalid. Only "
                "instances of `wagtail.wagtailcore.blocks.Block` may be "
                "registered with the the block_registry.".format(attr_name)
            )

    def register_block(self, attr_name, block):
        """
        Registers `block` to `attr_name` in the registry.
        """

        self._verify_block(attr_name, block)
        self._registry[attr_name] = block

    def unregister_block(self, attr_name):
        """
        Unregisters the block associated with `attr_name` from the registry.

        If no block is registered to `attr_name`, NotRegistered will raise.
        """
        if attr_name not in self._registry:
            raise NotRegistered(
                'There is no block registered as "{}" with the '
                'RegisteredBlockStreamFieldRegistry registry.'.format(
                    attr_name
                )
            )
        else:
            del self._registry[attr_name]

block_registry = RegisteredBlockStreamFieldRegistry()


def find_blocks():
    """
    Auto-discover INSTALLED_APPS registered_blocks.py modules and fail
    silently when not present. This forces an import on them thereby
    registering their blocks.

    This is a near 1-to-1 copy of how django's admin application registers
    models.
    """

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's sizedimage module.
        try:
            before_import_block_registry = copy.copy(
                block_registry._registry
            )
            import_module('{}.registered_blocks'.format(app))
        except:
            # Reset the block_registry to the state before the last
            # import as this import will have to reoccur on the next request
            # and this could raise NotRegistered and AlreadyRegistered
            # exceptions (see django ticket #8245).
            block_registry._registry = before_import_block_registry

            # Decide whether to bubble up this error. If the app just
            # doesn't have a stuff module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'registered_blocks'):
                raise
