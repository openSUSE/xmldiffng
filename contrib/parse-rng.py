#!/usr/bin/env python2

from __future__ import print_function
from lxml import etree
import json
import logging
import sys

# Dictionary for prefix -> namespace URI mapping
NSMAP = dict(rng="http://relaxng.org/ns/structure/1.0",
             a="http://relaxng.org/ns/compatibility/annotations/1.0",
             )

RNGREF = etree.QName(NSMAP['rng'], "ref")
DEFVALUE = etree.QName(NSMAP['a'], "defaultValue")

# Logging stuff
log = logging.getLogger('rngparser')
log.setLevel(logging.INFO)
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
log.addHandler(handler)


def hasattribute(node):
    """Tests the current node, if it contains a <attribute> element
    
    :param node: the current node
    :type node: :class:`lxml.etree._Element`
    :return: True if the current node contains a a <attribute> element,
             False otherwise
    :rtype: bool
    """
    return bool(node.xpath("rng:attribute", namespaces=NSMAP))


def getelementname(node):
    """Returns the element name from a define

    :param node: the current node
    :type node: :class:`lxml.etree._Element`
    :return: string of element name
    :rtype: str
    """
    return node.find("rng:element", namespaces=NSMAP)


def getattribute(node):
    """Get the default attribute and value of the current node
    
    :param node: the current node
    :type node: :class:`lxml.etree._Element`
    :return: tuple of default attribute name and its value
    :rtype: tuple
    """
    attribute = node.find("rng:attribute", namespaces=NSMAP)
    # Maybe we should check, if attribute/name is available
    name = attribute.attrib.get('name')
    if name is None:
        return
    log.info("   Attribute %s", name)
    if DEFVALUE.text in attribute.attrib:
        defaultvalue = attribute.attrib[DEFVALUE.text]
        log.info("   default value %s", defaultvalue)
        return (name, defaultvalue)


def visitsingleref(ref, visited, definedict):
    """Visit a single <ref/>
    
    :param ref: the current <ref/> node
    :type ref: :class:`lxml.etree._Element`
    :param visited: the set of visited references
    :type visited: set
    :param definedict: dictionary of all definition with maps from a name to the node
    :type definedict: dict
    """
    refname = ref.attrib['name']
    log.info( "   ref detected: %s", refname)
    if refname in visited:
        return
    visited.add(refname)
    define = definedict.get(refname)
    if define is None:
        # Really?
        return
    log.debug("     %s", visited)
    if hasattribute(define):
        # try to discover attribute
        # log.info("   Attribute node found")
        return getattribute(define)
    
    for r in define.iter(RNGREF.text):
        log.info("   ref: %s" % r.attrib['name'])
        return visitsingleref(r, visited, definedict)


def visitrefs(element, definedict):
    """Visit all <ref/> elements contained in the current element definition
    
    :param element: the current element node
    :type element: :class:`lxml.etree._Element`
    :param definedict: dictionary of all definition with maps from a name to the node
    :type definedict: dict
    
    """
    visited = set()
    attributes = list()
    for ref in element.iter(RNGREF.text):
        attr = visitsingleref(ref, visited, definedict)
        attributes.append(attr)
    log.info("visitrefs: %s", attributes)
    return attributes


def parserng(rngfilename):
    """Read RNG file and return a dictionary in the format of
       { 'element': [ (name1, value1), ...], }

     :param rngfilename: path to the RNG file (in XML format)
     :type rngfilename: str
     :return: result dictionary
     :rtype: dict
    """
    rngtree = etree.parse(rngfilename)
    # Maybe there is a more efficient method:
    rngelements = rngtree.xpath("//rng:define[rng:element]", namespaces=NSMAP)
    alldefines = rngtree.xpath("//rng:define[not(rng:element)]", namespaces=NSMAP)
    definedict = {node.attrib['name']: node for node in alldefines}

    elements = dict()
    for node in rngelements:
        element = getelementname(node)
        if element is not None:
            name = element.attrib.get('name')
            log.info("Element definition: %s -> %s", node.attrib['name'], name)
            attr = visitrefs(node, definedict)
            elements[name] = attr

    #
    #with open("rng.json", 'w') as fh:
    #    json.dump(elements, fh)
    log.info("Result: %s", elements)


if __name__ == "__main__":
    try:
        parserng(sys.argv[1])
    except IndexError:
        log.error("Expect an RNG schema")
        sys.exit(10)
