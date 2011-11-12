#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from lxml import etree
import logging
import sys
import os
from PmsRequestHandler import *

class BaseMetadataParser(object):
    """docstring for BaseMetadataParser"""
    def __init__(self, opts):
        self.opts = opts
    #end def __init__
    
    def array_of_attributes_with_key_from_child_nodes_with_name(self, node, node_name, key):
        result = [""]
        subnodes = node.findall(node_name)
        if len(subnodes) > 0:
            result = map(lambda n: n.attrib[key], subnodes)
        return result
    #end def array_of_attributes_with_key_from_child_nodes_with_name
    
    def new_tag_string_entry(self, key, value):
        try:
            #example: " blah blah: it's time to {come} home blah   "
            #becomes: "blah blah&#58; it's time to &#123;come&#125; home blah"
            cleaned_up_value = value.strip()
            cleaned_up_value = cleaned_up_value.replace('{', "&#123;")
            cleaned_up_value = cleaned_up_value.replace('}', "&#125;")
            cleaned_up_value = cleaned_up_value.replace(':', "&#58;")
            #example: "'{Long Description:blah blah...}'"
            return '{%s:%s}' % (key, value.strip())
        except AttributeError, e:
            return ""
        #end try
    #end def new_tag_string_entry
#end class MetadataParser