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
    
    def array_of_attributes_with_key_from_child_nodes_with_name(self, video, node_name, key):
        result = [""]
        nodes = video.findall(node_name)
        if len(nodes) > 0:
            result = map(lambda n: n.attrib[key], nodes)
        return result
    #end def arrayOfTagAttributesFromNodesWithName
#end class MetadataParser