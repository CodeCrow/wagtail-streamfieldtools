from __future__ import unicode_literals

from django.conf import settings
from django.template import Template
from django.template.loader import get_template, TemplateDoesNotExist
from django.utils import six
from django.utils.encoding import force_text

WAGTAIL_RENDITION_SETS = getattr(settings, 'WAGTAIL_RENDITION_SETS', {})


class InvalidRendition(Exception):
    pass


class NoTemplateProvided(Exception):
    pass


class Rendition(object):

    def __init__(self, short_name, verbose_name, description,
                 path_to_template=None, template_string=None,
                 image_rendition=None):
        if six.PY2:
            short_name = force_text(short_name)

        self.short_name = short_name
        self.verbose_name = verbose_name
        self.description = description
        self.image_rendition = image_rendition or ''
        if path_to_template:
            try:
                template = get_template(path_to_template)
            except TemplateDoesNotExist:
                raise
            else:
                self._template = template
        elif template_string:
            template = Template(template_string)
            self._template = template
        else:
            raise NoTemplateProvided(
                "All Rendition instances must provide either a "
                "`path_to_template` or `template_string` argument."
            )

    def __str__(self):
        return self.verbose_name

    @property
    def template(self):
        return self._template


class RenditionMixIn(object):

    def __init__(self, *args, **kwargs):
        self._rendition = {}
        super(RenditionMixIn, self).__init__(*args, **kwargs)

    @property
    def rendition(self):
        return self._rendition or {}

    @rendition.setter
    def rendition(self, value):
        if not value:
            pass
        elif not isinstance(value, Rendition):
            raise InvalidRendition(
                'Renditions must be instances of streamfield_renditions.'
                'blocks.base.Rendition'
            )
        else:
            self._rendition = value
