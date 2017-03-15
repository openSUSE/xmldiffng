#!/usr/bin/env python2

from __future__ import print_function
from lxml import etree
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
    return bool(node.xpath("rng:attribute", namespaces=NSMAP))


def getattribute(node):
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
    """
    """
    refname = ref.attrib['name']
    # log.info( "   ref detected: %s", refname)
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
    """
    """
    visited = set()
    attributes = list()
    for ref in element.iter(RNGREF.text):
        attr = visitsingleref(ref, visited, definedict)
        attributes.append(attr)
    return attributes


def parserng(rngfilename):
    """
    """
    rngtree = etree.parse(rngfilename)
    # Maybe there is a more efficient method:
    rngelements = rngtree.xpath("//rng:define[rng:element]", namespaces=NSMAP)
    alldefines = rngtree.xpath("//rng:define[not(rng:element)]", namespaces=NSMAP)
    definedict = {node.attrib['name']: node for node in alldefines}
    
    elements = dict()
    for element in rngelements:
        log.info("Element definition: %s", element.attrib['name'])
        attr = visitrefs(element, definedict)
        elements[element.tag] = attr
    log.info("Result: %s", elements)
        

if __name__ == "__main__":
    try:
        parserng(sys.argv[1])
    except IndexError:
        log.error("Expect an RNG schema")
        sys.exit(10)
