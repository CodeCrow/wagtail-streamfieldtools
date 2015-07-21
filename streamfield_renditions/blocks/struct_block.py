from __future__ import unicode_literals

from django.template.loader import render_to_string

from wagtail.wagtailcore.blocks import StructBlock, StructValue, TextBlock

from .base import WAGTAIL_RENDITION_SETS, UnavailableRenditionSet
from .field_block import RenditionSetChoiceBlock


class RenditionAwareStructBlock(StructBlock):

    def __init__(self, rendition_set, local_blocks, **kwargs):
        try:
            rendition_set_config = WAGTAIL_RENDITION_SETS[rendition_set]
        except KeyError:
            raise UnavailableRenditionSet(
                'No Rendition set found with key {}'.format(rendition_set)
            )
        self._rendition_set_config = rendition_set_config
        local_blocks.append(
            (
                'addl_classes',
                TextBlock(
                    label='Additional Classes',
                    required=False,
                    help_text="Enter any additional classes you'd like to add "
                              "to this module's containing div."
                )
            )
        )
        local_blocks.append(
            (
                'render_as',
                RenditionSetChoiceBlock(
                    rendition_set_config=rendition_set_config,
                    label='Render As',
                    required=True,
                    help_text='How this module should be rendered.'
                )
            )
        )

        super(RenditionAwareStructBlock, self).__init__(
            local_blocks=local_blocks,
            **kwargs
        )

    def render(self, value):
        """
        Finds the appropriate rendition
        """
        rendition = self._rendition_set_config.get(
            value['render_as']
        )
        template = rendition.get('path_to_template')
        return render_to_string(
            template,
            {
                'self': value,
                'image_rendition': rendition.get(
                    'image_rendition', 'original'
                ),
                'addl_classes': value['addl_classes']
            }
        )

    def to_python(self, value):
        # This is where the rendition needs to be injected.
        # Blocks used by RenditionStructBlock must have a to_python method
        # that can either accept **kwargs or an extra kwarg named `rendition`
        struct_value_list = []
        for name, child_block in self.child_blocks.items():
            if name in value:
                child_block.rendition = self._rendition_set_config.get(
                    value['render_as']
                )
                to_append = child_block.to_python(value[name])
            else:
                to_append = child_block.get_default()
            struct_value_list.append((name, to_append))
        return StructValue(self, struct_value_list)
