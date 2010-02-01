"""
Initialize ZAnnot Product

Author: Brent Hendricks
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import ZAnnot

def initialize(context):
    """
    Register base classes
    """
    context.registerClass(ZAnnot.ZAnnot,
                          constructors=(ZAnnot.manage_addZAnnotForm,
                                        ZAnnot.manage_addZAnnot),
                          icon="www/annotationFolder.gif")
                          
    context.registerClass(ZAnnot.ZAnnotation,
                          permission="ZAnnot: Add Annotation",
                          constructors=(ZAnnot.manage_addZAnnotationForm,
                                        ZAnnot.manage_addZAnnotation),
                          icon="www/annotation.gif")
