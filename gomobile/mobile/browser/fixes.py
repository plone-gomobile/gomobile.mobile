"""

    Misc. hacks to Plone to improve mobiReady test scores
    
    http://mobiready.com

"""


#
# Fix generating of empty CSS classes
#
from Acquisition import aq_inner, aq_base
from archetypes.kss.fields import ATFieldDecoratorView as _ATFieldDecoratorView

class ATFieldDecoratorView(_ATFieldDecoratorView):
    
    def getKssClasses(self, fieldname, templateId=None, macro=None, target=None):
        context = aq_inner(self.context)
        field = context.getField(fieldname)
        # field can be None when widgets are used without fields
        # check whether field is valid
        if field is not None and field.writeable(context):
            classstring = ' kssattr-atfieldname-%s' % fieldname
            if templateId is not None:
                classstring += ' kssattr-templateId-%s' % templateId
            if macro is not None:
                classstring += ' kssattr-macro-%s' % macro
            if target is not None:
                classstring += ' kssattr-target-%s' % target
            # XXX commented out to avoid macro showing up twice
            # not removed since it might be needed in a use case I forgot about
            # __gotcha
            #else:
            #    classstring += ' kssattr-macro-%s-field-view' % fieldname
        else:
            classstring = 'kss-dummy' # TODO don't let emptry string through
        return classstring

def getKssClasses(self, fieldname, templateId=None, macro=None, target=None):
        context = aq_inner(self.context)
        field = context.getField(fieldname)
        # field can be None when widgets are used without fields
        # check whether field is valid
        if field is not None and field.writeable(context):
            classstring = ' kssattr-atfieldname-%s' % fieldname
            if templateId is not None:
                classstring += ' kssattr-templateId-%s' % templateId
            if macro is not None:
                classstring += ' kssattr-macro-%s' % macro
            if target is not None:
                classstring += ' kssattr-target-%s' % target
            # XXX commented out to avoid macro showing up twice
            # not removed since it might be needed in a use case I forgot about
            # __gotcha
            #else:
            #    classstring += ' kssattr-macro-%s-field-view' % fieldname
        else:
            classstring = 'kss-dummy' # TODO don't let emptry string through
        return classstring    
    
def getKssClassesInlineEditable(self, fieldname, templateId, macro=None, target=None):
    classstring = self.getKssClasses(fieldname, templateId, macro, target)
    global_kss_inline_editable = self._global_kss_inline_editable()
    if global_kss_inline_editable and classstring != "kss-dummy":
        classstring += ' inlineEditable'
        
    if classstring == "": classtring = "kss-dummy"
    return classstring
    
    
# Monkey patch the fuckiny thing
_ATFieldDecoratorView.getKssClasses = getKssClasses
_ATFieldDecoratorView.getKssClassesInlineEditable = getKssClassesInlineEditable