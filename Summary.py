#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from datetime import datetime

class Summary:
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state
        
        if not 'time_start' in self.__dict__:
            self.time_start = datetime.now()
            self.datetimeformat = "%Y-%m-%d_%H:%M:%S"
            
            self.items_processed = 0
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
        
        total_items = self.metadata_removal_success+self.metadata_removal_fail
        if total_items > 0:
            results.append("Metadata cleared: \t\t%d, \tFailed: %d, \tTotal: %d" % ( self.metadata_removal_success, self.metadata_removal_fail, total_items ))
        
        total_items = self.metadata_embedded_success+self.metadata_embedded_fail
        if total_items > 0:
            results.append("Metadata embedded: \t\t%d, \tFailed: %d, \tTotal: %d" % ( self.metadata_embedded_success, self.metadata_embedded_fail, total_items ))
        
        total_items = self.metadata_optimized_success+self.metadata_optimized_fail
        if total_items > 0:
            results.append("Metadata optimized: \t\t%d, \tFailed: %d, \tTotal: %d" % ( self.metadata_optimized_success, self.metadata_optimized_fail, total_items ))
        
        total_items = self.subtitle_export_success+self.subtitle_export_success
        if total_items > 0:
            results.append("Subtitles exported: \t\t%d, \tFailed: %d, \tTotal: %d" % ( self.subtitle_export_success, self.subtitle_export_success, total_items ))
        
        total_items = self.artwork_export_success+self.artwork_export_fail
        if total_items > 0:
            results.append("Artwork exported: \t\t%d, \tFailed: %d, \tTotal: %d" % ( self.artwork_export_success, self.artwork_export_fail, total_items ))
        
        results.append("Items processed: \t\t%d" % ( self.items_processed ))
            
        duration = str(now_time - self.time_start).split('.')[0]
        results.append("Execution Duration: \t\t%s" % duration)
        return results
    
    def increment_items_processed(self):
        self.items_processed += 1
    
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

