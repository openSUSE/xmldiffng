#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from lxml import etree

RNGFILE = "geekodoc5-flat.rng"

A = u'http://relaxng.org/ns/compatibility/annotations/1.0'
RNG = u"http://relaxng.org/ns/structure/1.0"

defaultValue = etree.QName("{%s}defaultValue" % A)

NSDICT = dict(rng=RNG, a=A)

def parserng(rngfile):
    """Parse RNG file and returns a set of attributes with default
       values
    """
    rngtree = etree.parse(rngfile)

    attributes = set()
    for node in rngtree.iter():
        # print(node)
        if defaultValue in node.attrib:
            name = node.attrib.get('name')
            default = node.attrib.get(defaultValue)
            attributes.add(name + " (" + default + ")")
    return attributes


if __name__ == "__main__":
    result = parserng(RNGFILE)
    print("Attributes:", result)
