#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from datetime import datetime
import logging

class Statistics:
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state
        
        if not 'time_start' in self.__dict__:
            self.time_start = datetime.now()
            self.datetimeformat = "%Y-%m-%d_%H:%M:%S"
            
            self.metadata_removal_success = 0
            self.metadata_removal_fail = 0
            self.metadata_embedded_success = 0
            self.metadata_embedded_fail = 0
            self.metadata_optimized_success = 0
            self.metadata_optimized_fail = 0
            self.subtitle_export_success = 0
            self.subtitle_export_fail = 0
            self.artwork_export_success = 0
            self.artwork_export_fail = 0

    def results(self):
        now_time = datetime.now()
        results = [] 
        
        results.append("Metadata cleared: \t%d, Failed: %d, Total: %d" % ( self.metadata_removal_success, self.metadata_removal_fail, (self.metadata_removal_success+self.metadata_removal_fail) ))
        results.append("Metadata embedded: \t%d, Failed: %d, Total: %d" % ( self.metadata_embedded_success, self.metadata_embedded_fail, (self.metadata_embedded_success+self.metadata_embedded_fail) ))
        results.append("Metadata optimized: \t%d, Failed: %d, Total: %d" % ( self.metadata_optimized_success, self.metadata_optimized_fail, (self.metadata_optimized_success+self.metadata_optimized_fail) ))
        results.append("Subtitles exported: \t%d, Failed: %d, Total: %d" % ( self.subtitle_export_success, self.subtitle_export_success, (self.subtitle_export_success+self.subtitle_export_success) ))
        results.append("Artwork exported: \t%d, Failed: %d, Total: %d" % ( self.artwork_export_success, self.artwork_export_fail, (self.artwork_export_success+self.artwork_export_fail) ))
        
        duration = str(now_time - self.time_start).split('.')[0]
        results.append("Duration: %s" % duration)
        return results
    
    def metadata_removal_succeeded(self):
        self.metadata_removal_success += 1

    def metadata_removal_failed(self):
        self.metadata_removal_fail += 1
    
    def metadata_embedded_succeeded(self):
        self.metadata_embedded_success += 1
        
    def metadata_embedded_failed(self):
        self.metadata_embedded_fail += 1
        
    def metadata_optimized_succeeded(self):
        self.metadata_optimized_success += 1

    def metadata_optimized_failed(self):
        self.metadata_optimized_fail += 1
        
    def subtitle_export_succeeded(self):
        self.subtitle_export_success += 1
        
    def subtitle_export_failed(self):
        self.subtitle_export_fail += 1
        
    def artwork_export_succeeded(self):
        self.artwork_export_success += 1

    def artwork_export_failed(self):
        self.artwork_export_fail += 1

