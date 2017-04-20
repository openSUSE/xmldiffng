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

RNGATTRIBUTE = etree.QName(NSMAP['rng'], "attribute")
RNGREF = etree.QName(NSMAP['rng'], "ref")
DEFVALUE = etree.QName(NSMAP['a'], "defaultValue")

# Logging stuff
log = logging.getLogger('rngparser')
log.setLevel(logging.INFO)
formatter = logging.Formatter('[%(levelname)-7s] %(message)s')
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


def getsingleattribute(attribute):
    """Get the single default attribute and value of the current
       define node

    :param node: the current define node
    :type node: :class:`lxml.etree._Element`
    :return: tuple of default attribute name and its value
    :rtype: tuple
    """
    # attribute = node.find("rng:attribute", namespaces=NSMAP)
    # Maybe we should check, if attribute/name is available
    attrname = attribute.attrib.get('name')
    # Special case for attributes with <anyName/>:
    if attrname is None:
        return
    log.debug ("   => Attribute found %r", attrname)
    # HINT: Enable the following line, if you want _all_ attributes:
    # return attrname
    if DEFVALUE.text in attribute.attrib:
        defaultvalue = attribute.attrib[DEFVALUE.text]
        log.info("   default value %s->%r", attrname, defaultvalue)
        return (attrname, defaultvalue)


def getattributes(node):
    """Get the all default attributes from the current define node

    :param node: the current define node
    :type node: :class:`lxml.etree._Element`
    :return: list of tuples of default attribute name and its value
    :rtype: list
    """
    result = []
    for attribute in node.iter(RNGATTRIBUTE.text):
        log.debug("   see %s", attribute.attrib.get('name'))
        x = getsingleattribute(attribute)
        if x:
            result.append(x)
    return result


def visitsingleref(ref, define, visited, definedict):
    """Visit a single <ref/> and follow it through the <attribute> node

    :param ref: the current <ref/> node
    :type ref: :class:`lxml.etree._Element`
    :param define: the node pointing to the <define>
    :type define: :class:`lxml.etree._Element`
    :param visited: the set of visited references
    :type visited: set
    :param definedict: dictionary of all definition with maps from a name to the node
    :type definedict: dict
    :return: name of a found attribute or None
    :rtype: str | None
    """
    refname = ref.attrib['name']
    log.debug("    ref %s visited=%s", refname, refname in visited)
    log.debug("    define %s found", define.attrib.get('name'))

    if hasattribute(define):
        # try to discover attribute
        log.debug("   Attribute node found %s", define.attrib.get('name'))
        return getattributes(define)


def visitrefs(element, attributes, definedict):
    """Visit all <ref/> elements contained in the current element definition

    :param element: the current element node
    :type element: :class:`lxml.etree._Element`
    :param definedict: dictionary of all definition with maps from a name to the node
    :type definedict: dict
    :return: list of all attributes
    :rtype: list
    """
    visited = set()
    refs = list(element.iter(RNGREF.text))
    log.debug("Found %i refs: %s", len(refs), [r.attrib.get('name') for r in refs])

    for ref in element.iter(RNGREF.text):
        log.debug("  visit %s...", ref.attrib.get('name'))

        refname = ref.attrib['name']
        define = definedict.get(refname)
        if define is None:
            continue

        result = getattributes(define)
        if result:
            attributes.extend(result)

        if refname not in visited:
            visited.add(refname)
            attr = visitsingleref(ref, define, visited, definedict)
            if attr:
                log.debug("  got %r attribute", attr)
                attributes.append(attr)

        result = visitrefs(define, attributes, definedict)
        if not result:
            attributes.extend(result)

    return attributes


def parserng(rngfilename, elementdef=None):
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

    if elementdef is not None:
        node = rngtree.find("//rng:define[rng:element][@name='%s']" % elementdef,
                            namespaces=NSMAP)
        if node is None:
            log.error("Could not find %r in %s", elementdef, rngfilename)
            sys.exit(10)

        rngelements = [node]

    elements = dict()
    for node in rngelements:
        attributes = list()
        element = getelementname(node)
        if element is not None:
            name = element.attrib.get('name')
            log.info("** Element definition: %s -> %s", node.attrib['name'], name)
            attr = visitrefs(node, attributes, definedict)
            log.info("  ==> Attributes: %s", attr)
            elements[name] = attr
            log.info("--------------------")

    #
    from collections import OrderedDict
    selem = OrderedDict()
    selements = OrderedDict((key, elements[key])
                            for key in sorted(elements.keys()))

    with open("rng.json", 'w') as fh:
        json.dump(selements, fh)
    # log.info("Result: %s", elements)
    # Pretty-print JSON, do:
    # $ cat rng.json | python3 -m json.tool


if __name__ == "__main__":
    try:
        try:
            elementdef = sys.argv[2]
        except:
            elementdef = None
        parserng(sys.argv[1], elementdef)
    except IndexError:
        log.error("Expect an RNG schema")
        sys.exit(10)
