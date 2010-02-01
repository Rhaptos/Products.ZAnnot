"""
ZAnnot.py - Zope Annotation Server

Author: Brent Hendricks and Yasushi Yamazaki
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import xml.parsers.expat

# FIXME: This module needs to go through a code audit


# Annotation RDF Parser ---------------------------
class AnnotRequestParser:
    """Parses the annotation RDF given by the annotation client, as a part of
       new/update request.
    
       Returns a map with keys:
         type,annotates,context,title,language,creator,created,date,root,inreplyto,
         body (body uri or content), isBodyUri (flag specifying whether the body is an uri)
         
       Note:
       - for the tags in self.tagnames, it will use the "resource" attribute content
         if that is given; if not, it will use the tag contents.
       - if <body> has a resource attribute, then that specifies a body uri.
         if <body> has no resource string but has a <Body> inside, then that
         specifies a body content.
       - for a regular annotation, "root" and "inreplyto" will be empty.
         and for the thread reply case, "annotates" will be empty.
       - "type" only contains the second <type> tag content - first one is usually a
         "Annotation" or "Reply", and second one is "Comment", "Example", etc.
         so we really only care about the second one, since we already know
         if it is an annotation or a reply, by the presence of <annotates> or <root>.
       """

    # annotation namespaces
    namespaces = ["http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                  "http://www.w3.org/2000/10/annotation-ns#",
                  "http://www.w3.org/2001/03/thread#",
                  "http://www.w3.org/1999/xx/http#",
                  "http://purl.org/dc/elements/1.0/",
                  "http://purl.org/dc/elements/1.1/"]
    # tags to catch (value is its possible namespace(s), OR-separated)
    tagnames = {"type": [namespaces[0]],
                "annotates": [namespaces[1]],
                "context": [namespaces[1]],
                "title": [namespaces[4],namespaces[5]],
                "language": [namespaces[4],namespaces[5]],
                "creator": [namespaces[4],namespaces[5]],
                "created": [namespaces[1]],
                "date": [namespaces[4],namespaces[5]],
                "root": [namespaces[2]],
                "inReplyTo": [namespaces[2]]}
    # namespace separator
    separator = '*'

    def __init__(self, raw_data):
        # content to parse
        self.raw_data = raw_data
        # tag content holder
        # they are stored as lists because some tags may appear more than once
        self.tagcontents = {}
        # set default values
        for tag in self.tagnames.keys():
            self.tagcontents[tag] = ''
        self.tagcontents["title"] = "No Title"
        self.tagcontents["language"] = "en"
        self.body = ''
        self.bodyIndex = {'begin':0, 'end':0}
        self.isBodyUri = 0
        # PARSER
        self.p = xml.parsers.expat.ParserCreate("UTF-8",self.separator)
        # buffer
        self.charBuffer = ''

    def getLocalName(self, name):
        """Namespace and local name are separated by 'self.separator'"""
        if name.find(self.separator) != -1:
            (ns,name) = name.split(self.separator)
            return (str(ns), str(name))
        return ('', str(name))

    def getAttribute(self, attrs, name):
        """Get an attribute."""
        result = ''
        for key in attrs.keys():
            (prefix, attr) = self.getLocalName(key)
            if attr==name:
                result = str(attrs[key])
        return result

    def startElement(self, name, attrs):
        """Catch tag attributes"""
        (ns, name) = self.getLocalName(name)
        if self.tagnames.has_key(name) and ns in self.tagnames[name]:
            res = self.getAttribute(attrs, "resource")
            if res:
                self.tagcontents[name] = res
        elif ns==self.namespaces[1] and name=="body":
            res = self.getAttribute(attrs, "resource")
            if res:
                # resource sting found
                self.body = res
                self.isBodyUri = 1
            else:
                # annotation text given
                self.isBodyUri = 0
        elif ns==self.namespaces[3] and name=="Body":
            # <Body> in http namespace
            context = self.p.GetInputContext()

            # The first byte of the body is the current index + the end of the <Body> tag + 1
            self.bodyIndex['begin'] = self.p.ErrorByteIndex + context.index('>') + 1

    def charData(self, data):
        """Catch tag contents"""
        self.charBuffer = data

    def endElement(self, name):
        """Catch tag contents"""
        (ns,name) = self.getLocalName(name)
        if self.tagnames.has_key(name) and ns in self.tagnames[name] and self.charBuffer.strip():
            # appending, in case there are multiple tags of this kind
            self.tagcontents[name] = self.charBuffer
        elif not self.isBodyUri and ns==self.namespaces[3] and name=="Body":
            self.bodyIndex['end'] = self.p.ErrorByteIndex
            

    def parse(self):
        """Parse the annotation RDF."""
        # parse
        self.p.StartElementHandler = self.startElement
        self.p.CharacterDataHandler = self.charData
        self.p.EndElementHandler = self.endElement
        self.p.Parse(self.raw_data)
        # if body text is given
        if not self.isBodyUri:
            self.body = self.raw_data[self.bodyIndex['begin'] : self.bodyIndex['end']]
        # create resultset ------------------------
        r = {"body": self.body, "isBodyUri": self.isBodyUri}
        for tag in self.tagnames.keys():
            r[tag.lower()] = self.tagcontents.get(tag, '')
        # return
        return r

