"""
ZAnnot.py - Zope Annotation Server

Author: Brent Hendricks
(C) 2002-2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

# This is a PythonScript function that process user requests
# It's implemented as a PythonScript so that it runs as restricted code
                      

method = context.REQUEST['REQUEST_METHOD']
# call appropriate routines
if method == "GET" and context.REQUEST.has_key('w3c_annotates'):
    target = context.REQUEST.form['w3c_annotates']
    replyTree = context.REQUEST.form.get('w3c_replyTree', None)
    objs = context.queryAnnotation(target, replyTree)
    return context.annotationRDF(annotations = objs)

elif method == "POST":
    (content, encoding, id) = context.parseRequest(context.REQUEST)

    # If there's no ID, it's a new annotation
    if not id:
        return context.addAnnotation(content, encoding)

    # Otherwise, try to update the old one
    try:
        annotation = context[id]
    except KeyError:
        raise "Bad Request", "No such annotation: %s" % id
    
    return annotation.update(content, encoding)
