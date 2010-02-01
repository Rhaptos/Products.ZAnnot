ZAnnot Annotation Server for Zope

  Overview

    ZAnnot is an annotation server for Zope, allowing clients to add
    annotations to web pages without editing their source.  It uses
    the Annotea protocol defined by the World Wide Web Consortium
    (http://www.w3.org/2001/Annotea/) and should work with any Annotea
    compatible client.  These include:

    - Amaya 6.2 and above (http://www.w3.org/Amaya/)

    - Mozilla/Netscape with the Annozilla plugin (ttp://annozilla.mozdev.org/)

    - IE with the Snufkin extension (http://jibbering.com/snufkin.html)

    although we have only tested it with Amaya and Annozilla.

  Installation

    Extract the ZAnnot tarfile into the Products directory of your
    Zope installation, and restart Zope.

  Setting up your annotation server

    Add an instance of the 'Annotation Server' object somewhere in
    your Zope site.  That's it, you're ready to go!  You may want to
    create accounts for users allowed to post annotations.  See the
    Zope documentation for instructions on how to create and manage
    users.

    For some ideas on how to set up security for ZAnnot, please read
    security.txt

  How it works

    An annotation client (such as a browser) posts an annotation to
    the server, giving it:

    1) The URL of the page being annotated

    2) The location of the annotation in the document (using XPointer)

    3) The body of the annotation

    ZAnnot stores this in an Annotation object in the Annotation
    Server folder on your site.  Future clients that visit the page
    can query the annotation server for a list of annotations relevant
    to that page.  The client will usually provide some visual
    indication that there is an annotation present, giving the user
    some opportunity to view it.

  Feedback

   If you have any questions, problems, or suggestions, please feel
   free to contact me at brentmh@rice.edu

  Enjoy!!!

  Copyright 2002, Brent Hendricks (brentmh@rice.edu)


  Brent Hendricks
  The Connexions Project (http://cnx.rice.edu)
  Rice University (http://www.rice.edu)