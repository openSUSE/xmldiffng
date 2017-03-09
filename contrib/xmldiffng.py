"""
This file contains a parser to extract the elements and attributes with their values from a given RELAX NG file.
The goal is to achieve information about what attributes do have default values.
Afterwards these attributes need to get matched with their partner in the supported XML file.
"""

from xml.sax import make_parser, handler

# location of the RELAX NG file
rngfile = "./geekodoc5-flat.rng"

class RelaxHandler(handler.ContentHandler):

    def __init__(self):
        self.attributes = set()
        self.attribname = " "
        self.defaultValue = " "

    def startElement(self, name, attrs):
        # check if current node has a defaultValue in its attributes
        if "a:defaultValue" in attrs:
            # save the name of the attribute
            self.attribname = attrs["name"]
            # save the default value of the attribute
            self.defaultValue = attrs["a:defaultValue"]
            # save current attribute (with defaultValue if set)
            self.attributes.add(self.attribname + " (" + self.defaultValue + ")")

    def getAttributes(self):
        return self.attributes

parser = make_parser()
rng = RelaxHandler()
parser.setContentHandler(rng)
parser.parse(rngfile)

print("Attributes:")
print(rng.getAttributes())
