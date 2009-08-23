"""
    Mobile behavior for content.

"""

__author__  = 'Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>'
__author_url__ = "http://www.twinapex.com"
__docformat__ = 'epytext'
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL v2"

from zope import schema
from zope.interface import implements, alsoProvides
from zope.component import adapts
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema import getFields

from plone.directives import form

class IMobileBehavior(form.Schema):
    """ How content and its children react to differt medias """

    form.fieldset(
        'mobile',
        label=('Mobile'),
        fields=('mobileFolderListing'),
    )

    mobileFolderListing = schema.Bool(title=u"Mobile folder listing",
                                  description=u"Show touch screen friendly listing of the child content at the bottom of the page.",
                                  default=True)



alsoProvides(IMobileBehavior, form.IFormFieldProvider)


_marker = object()

class FieldPropertyDelegate(object):
    """ Store values in inst.context

    Normal FieldPropery will store on inst.
    This allows storing properties on attributes of some other
    object called context.
    """

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__

        self.__field = field
        self.__name = name

    def __get__(self, inst, klass):
        if inst is None:
            return self

        value = inst.context.__dict__.get(self.__name, _marker)
        if value is _marker:
            field = self.__field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self.__name)

        return value

    def __set__(self, inst, value):
        field = self.__field.bind(inst.context)
        field.validate(value)
        if field.readonly and inst.context.__dict__.has_key(self.__name):
            raise ValueError(self.__name, 'field is readonly')
        inst.context.__dict__[self.__name] = value

    def __getattr__(self, name):
        return getattr(self.__field, name)

class MobileBehaviorStorage(object):
    """Set moible specific field properties on the context object and return the context object itself.#

    This allows to use attribute storage with schema input validation.
    """

    mobileFolderListing = FieldPropertyDelegate(IMobileBehavior["mobileFolderListing"])

    def __init__(self, context):
        self.context = context
