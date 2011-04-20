#
# ZAnnot.py - Zope Annotation Server
#
# Code by Yasushi Yamazaki and Brent Hendricks
#
# (C) 2002 Brent Hendricks - licensed under the terms of the
# GNU General Public License (GPL).  See LICENSE.txt for details

from OFS.Folder import Folder
from OFS.Image import File
from OFS.History import Historical
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import getSecurityManager, ClassSecurityInfo
from DateTime import DateTime
from AnnotRequestParser import AnnotRequestParser
from PythonScriptFile import PythonScriptFile
from Persistence import Persistent
import re

charset_re=re.compile(r'[0-9a-z]+/[0-9a-z]+\s*;\s*charset=([-_0-9a-z]+)(?:(?:\s*;)|\Z)',re.IGNORECASE)

### add interface ############################
manage_addZAnnotationForm = PageTemplateFile('zpt/manage_addZAnnotationForm',
                                             globals(),
                                             __name__='manage_addZAnnotationForm')

def manage_addZAnnotation(self, id, file='', title='', content_type='', properties={}, REQUEST=None):
    """Creates a new ZAnnotation object 'id' with the contents of 'file'"""

    id=str(id)
    title=str(title)

    self=self.this()

    # First, we create the file without data:
    self._setObject(id, ZAnnotation(id, title, properties))

    # Now we "upload" the data.  By doing this in two steps, we
    # can use a database trick to make the upload more efficient.
    if file:
        self._getOb(id).manage_upload(file)
    if content_type:
        self._getOb(id).content_type=content_type

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')


class ZAnnotation(File, Historical):
    """ZAnnotation"""

    meta_type = "Annotation"

    # Workgroup properties
    _properties=({'id':'title', 'type': 'string', 'mode': 'w'},
                 {'id':'content_type', 'type': 'string', 'mode': 'w'},
                 {'id':'type', 'type': 'string', 'mode': 'w'},
                 {'id':'annotates', 'type': 'string', 'mode': 'w'},
                 {'id':'context', 'type': 'string', 'mode': 'w'},
                 {'id':'language', 'type': 'string', 'mode': 'w'},
                 {'id':'creator', 'type': 'string', 'mode': 'w'},
                 {'id':'created', 'type': 'date', 'mode': 'w'},
                 {'id':'date', 'type': 'date', 'mode': 'w'},
                 {'id':'body', 'type': 'string', 'mode': 'w'},
                 {'id':'root', 'type': 'string', 'mode': 'w'},
                 {'id':'inreplyto', 'type': 'string', 'mode': 'w'},
                 {'id':'encoding', 'type':'string', 'mode': 'w'},
                 )

    security = ClassSecurityInfo()
 
    # Look and feel for management pages
    manage_look = PageTemplateFile('zpt/manage_look', globals(), __name__='manage_look')

    
    manage_options=(
        File.manage_options[0:1] +
        ({'label':'View', 'action':'annotationBody', 'help':('OFSP','File_View.stx')},
         )
        + File.manage_options[2:]
        + Historical.manage_options
        )

    def __init__(self, id, title, properties={}):
        """ZAnnotation constructor"""

        # Initialize properties
        if properties:
            self._doUpdate(properties)
        else:
            self.type = None
            self.annotates = None
            self.context = None
            self.language = None
            self.creator = None
            self.created = None
            self.date = None
            self.body = None
            self.root = None
            self.inreplyto = None
            self.encoding = ''

        return File.__init__(self, id, title,'','text/html')


    def __setstate__(self, state):
        """Upgrade annotation instances"""
        Persistent.__setstate__(self, state)

        # Put in encoding if it's missing
        if not hasattr(self, 'encoding'):
            self.encoding = ''

        # Change string dates to DateTime dates
        for property in self.propertyMap():
            id = property['id']
            if id not in ['date', 'created']: continue # Skip non-date properties
            if property['type'] == 'string':
                value = self.getProperty(id)
                self.manage_delProperties([id])
                try:
                    self.manage_addProperty(id, value, 'date')
                except:
                    self.manage_addProperty(id, '1970/01/01', 'date')

        # Ensure that date and created are valid DateTime 
        try:
            self.date = DateTime(self.date)
            self.created = DateTime(self.created)
        except:
            pass


    security.declarePublic('annotationBody')
    def annotationBody(self):
        """Return the annotation's body"""
        contentType = self.content_type
        if self.encoding:
            contentType = "%s; charset=%s" % (contentType, self.encoding)
        self.REQUEST.RESPONSE.setHeader('Content-Type', contentType)
        self.REQUEST.RESPONSE.setHeader('Cache-Control', 'max-age=84600, s-maxage=31536000, public, must-revalidate')
        return str(self.data)


    security.declarePublic('description')
    def description(self):
        """Returns the RDF description of the annotation"""
        return self.annotationRDF(annotations=[self])


    # Make description() the default method for viewing
    index_html = description


    security.declareProtected('ZAnnot: Edit Annotation', 'update')
    def PUT(self, REQUEST, RESPONSE):
        """Handle HTTP PUT method of updating annotations"""

        # FIXME: we should make sure the body exists
        content = str(REQUEST['BODY'])
        content_type = REQUEST.get_header('Content-Type')
        match = charset_re.match(content_type)
        if match:
            charset = match.group(1)
        else:
            charset = None

        self.update(content, charset)
        return self.description()


    security.declareProtected('ZAnnot: Edit Annotation', 'update')
    def update(self, content, encoding=None):
        """Update an annotation"""
        # Parse RDF and update ourself
        try:
            props = AnnotRequestParser(content).parse()
        except Exception,e:
            raise "Bad Request", "Error parsing supplied RDF: %s" % str(e)
        
        self._doUpdate(props)
        if encoding:
            self._updateProperty('encoding', encoding)

        # Send out reply
        self.REQUEST.RESPONSE.setHeader("Location", self.absolute_url())
        return self.postreplyRDF(result=self, location=self.absolute_url())


    security.declarePrivate('_doUpdate')
    def _doUpdate(self, props):
        """Actual update of the annotation body and properties"""

        # If the body isn't a URL, update the body text and blank out the body (the URL will get generated later)
        if not props["isBodyUri"]:
            self.update_data(props['body'])
            props['body'] = ''

        # Fill in user if not present
        if not props["creator"]:
            props["creator"] = getSecurityManager().getUser().getUserName()

        # Reformat date objects as DateTime
        props["created"] = DateTime(props["created"])
        props["date"] = DateTime(props["date"])        
	            
        for name in ["title", "type", "annotates", "context", "language", "creator", "created", "date", "body", "root", "inreplyto"]:
            self._updateProperty(name, props[name])


    def manage_beforeDelete(self, item, container):
        # removal is not allowed if it has a reply
        uri = self.absolute_url()
        
        all = container.objectValues('Annotation')
        replies = [a for a in all if (a.annotates == uri or a.root == uri or a.inreplyto == uri)]
        
        if replies:
            raise "Forbidden", "The annotation with a reply cannot be removed."


    # Provide permission defaults
    security.declareProtected('ZAnnot: Delete Annotation', 'DELETE')
    security.setPermissionDefault('ZAnnot: Edit Annotation', ('Manager', 'Owner',))
    security.setPermissionDefault('ZAnnot: Delete Annotation', ('Manager', 'Owner',))


manage_addZAnnotForm = PageTemplateFile("zpt/manage_addZAnnotForm", globals(), __name__="manage_addZAnnotForm")
                                        
def manage_addZAnnot(self, id, REQUEST=None):
    """Add a new ZAnnot object."""

    id = str(id)
    if not id:
        raise "Bad Request", "Please specify an ID."

    self = self.this()
    self._setObject(id, ZAnnot(id))

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect(self.absolute_url()+"/manage_main")


### class definition ##########################
class ZAnnot(Folder):
    """Annotation Server Product."""
    
    meta_type = "Annotation Server"

    security = ClassSecurityInfo()

    # Template for returning annotations
    annotationRDF = PageTemplateFile('zpt/annotation',globals(),__name__='annotation')
    annotationRDF.content_type="application/xml"
    annotationRDF_name = "annotation"

    # Template for annotation POST replies
    postreplyRDF = PageTemplateFile('zpt/postreply',globals(),__name__='postreply')
    postreplyRDF.content_type="application/xml"
    postreplyRDF_name = "postreply"

    # Restricted code for handling annotea requests
    index_html = PythonScriptFile('process', globals())


    def __init__(self,id):
        """ZAnnot Constructor"""
        self.id = id


    # Parse annotation request
    security.declarePublic('parseRequest')
    def parseRequest(self, REQUEST):
        """Parse an incoming annotation request"""

        # FIXME: we should make sure the body exists
        content = str(REQUEST['BODY'])
        content_type = REQUEST.get_header('Content-Type')
        match = charset_re.match(content_type)
        if match:
            charset = match.group(1)
        else:
            charset = None

        query = REQUEST.get('QUERY_STRING', '')
        if not query:
            return (content, charset, None)

        for param in query.split('&'):
            (key, value) = query.split('=')
            if key == "replace_source":
                id = value.split('/')[-1]
                break
        return (content, charset, id)



    # Primary actions
    security.declareProtected('ZAnnot: Add Annotation', 'addAnnotation')
    def addAnnotation(self, content, encoding=None):
        """Create an annotation."""

        id = "annot" + str(DateTime().timeTime())
        self.manage_addProduct["ZAnnot"].manage_addZAnnotation(id, content_type="text/html")

        # Update child with annotation data
        return getattr(self, id).update(content, encoding)


    security.declareProtected('Access contents information', 'queryAnnotation')
    def queryAnnotation(self, target, replyTree=None):
        """Search for annotations."""
        all = self.objectValues('Annotation')
        annotations = [a for a in all if a.annotates == target]
    
        if replyTree:
            annotations = [a for a in annotations if (a.root == replyTree or a.inreplyto == replyTree)]

        return annotations
        

    security.setPermissionDefault('ZAnnot: Add Annotation', ('Authenticated', 'Manager', 'Owner',))

InitializeClass(ZAnnotation)
InitializeClass(ZAnnot)
