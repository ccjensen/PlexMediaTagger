#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from BaseItem import *

class StreamItem(BaseItem):
    """docstring for StreamItem"""
    def __init__(self, opts, part_item, stream_element):
        super(StreamItem, self).__init__(opts)
        self.opts = opts
        self.part_item = part_item
        self.stream_element = stream_element
        
        self.id = self.stream_element.get('id', "")
        self.key = self.stream_element.get('key', "")
        self.stream_type = self.stream_element.get('streamType', "")        
        self.codec = self.stream_element.get('codec', "")
        self.channels = self.stream_element.get('channels', "")
        self.language = self.stream_element.get('language', "")
        self.language_code = self.stream_element.get('languageCode', "")
        
        self.stream_type_name = "Unknown"
        if self.stream_type == "1":
            self.stream_type_name = "Video"
        elif self.stream_type == "2":
            self.stream_type_name = "Audio"
        elif self.stream_type == "3":
            self.stream_type_name = "Subtitle"
        #end if
    #end def __init__
    
    def export_to_path(self, path):
        if self.key == "":
            logging.warning("cannot download asset")
            return None
        #end if
        
        request_handler = PmsRequestHandler()
        filename = os.path.basename(path)
        logging.info("downloading %s", filename)
        if not self.opts.dryrun:
            return request_handler.download_stream(path, self.key)
        #end if not dryrun
    #end def export_to_path
#end class StreamItem