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

class MetadataParser(object):
    """docstring for MovieMetadataParser"""
    def __init__(self, opts, videoMetadataContainer):
        self.opts = opts
        mediaContainer = videoMetadataContainer.getroot()
        videos = mediaContainer.getchildren()
        if len(videos) != 1:
            return
        #end if len
        self.video = videos[0]
        self.fileTypes = map(lambda x: os.path.splitext(x)[1], self.mediaPaths())
    #end def __init__
    
    def arrayOfAttributesWithKeyFromChildNodesWithName(self, video, nodeName, key):
        result = [""]
        nodes = video.findall(nodeName)
        if len(nodes) > 0:
            result = map(lambda n: n.attrib[key], nodes)
        return result
    #end def arrayOfTagAttributesFromNodesWithName
    
#     <Media id="49" duration="9701000" bitrate="4678" aspectRatio="1.78" audioChannels="2" audioCodec="aac" videoCodec="h264" videoResolution="1080" container="mov" videoFrameRate="24p">
# <Part id="49" key="/library/parts/49/Avatar%20(2009).m4v" duration="9701000" file="/Volumes/Drobo/Movies/Avatar (2009)/Avatar (2009).m4v" size="5810197410">
# <Stream id="37843" streamType="1" codec="h264" index="0" language="?" languageCode="und" />
# <Stream id="37844" streamType="2" selected="1" codec="aac" index="1" channels="2" language="English" languageCode="eng" />
# <Stream id="37845" streamType="3" index="2" language="English" languageCode="eng" />
# <Stream id="37846" streamType="3" index="3" language="?" languageCode="und" />
# </Part>
# </Media>

    def mediaPaths(self):
        mediaNode = self.video.find("Media")
        return self.arrayOfAttributesWithKeyFromChildNodesWithName(mediaNode, "Part", "file")
    #end isHD

    def isHD(self):
        mediaNode = self.video.find("Media")
        resolution = mediaNode.attrib['videoResolution']
        return resolution.isdigit() and int(resolution) >= 720
    #end isHD
    
    def tagString(self):
        return ""
    #end def tagString
    
    def newTagStringEntry(self, key, value):
        #example: "{'Long Description':'blah blah it\'s time to come home blah'}"
        return "{'%s':'%s'} " % (key, value.strip())
    #end def newTagStringEntry
#end class MetadataParser
    

class MovieMetadataParser(MetadataParser):
    """docstring for MovieMetadataParser"""
    def __init__(self, opts, videoMetadataContainer):
        super(MovieMetadataParser, self).__init__(opts, videoMetadataContainer)
        
        self.studio = self.video.get('studio', "")
        self.type = self.video.get('type', "")
        self.title = self.video.get('title', "")
        self.contentRating = self.video.get('contentRating', "") #PG-13, etc.
        self.summary = self.video.get('summary', "")
        self.rating = self.video.get('rating', "") #not used
        self.year = self.video.get('year', "")
        self.tagline = self.video.get('tagline', "")
        self.thumb = self.video.get('thumb', "")
        self.originallyAvailableAt = self.video.get('originallyAvailableAt', "")
        
        self.genreNames = self.arrayOfAttributesWithKeyFromChildNodesWithName(self.video, "Genre", "tag")
        if len(self.genreNames) > 0: 
            self.genre = self.genreNames[0] 
        else: 
            self.genre = ''
        self.genres = ', '.join(self.genreNames)
        
        self.writerNames = self.arrayOfAttributesWithKeyFromChildNodesWithName(self.video, "Writer", "tag")
        self.writers = ', '.join(self.writerNames)
        
        self.directorNames = self.arrayOfAttributesWithKeyFromChildNodesWithName(self.video, "Director", "tag")
        self.directors = ', '.join(self.directorNames)
        
        self.castNames = self.arrayOfAttributesWithKeyFromChildNodesWithName(self.video, "Role", "tag")
        self.cast = ', '.join(self.castNames)
    #end def __init__
    
    def tagString(self):        
        tagString = ""
        tagString += self.newTagStringEntry("Studio", self.studio)
        
        mediaType = ""
        if self.type == 'movie':
            mediaType = "Movie"
        elif self.type == 'show':
            mediaType = "TV Show"
        #end if self.type
        tagString += self.newTagStringEntry("Media Kind", mediaType)
        
        tagString += self.newTagStringEntry("Name", self.title)
        tagString += self.newTagStringEntry("Rating", self.contentRating)
        tagString += self.newTagStringEntry("Long Description", self.summary)
        tagString += self.newTagStringEntry("Release Date", self.originallyAvailableAt)
        tagString += self.newTagStringEntry("Description", len(self.tagline) > 0 if self.tagline else self.summary)

        tagString += self.newTagStringEntry("Genre", self.genre) #single genre
        tagString += self.newTagStringEntry("Screenwriters", self.writers)
        tagString += self.newTagStringEntry("Director", self.directors)
        tagString += self.newTagStringEntry("Cast", self.cast)
        
        hdValue = "%d" % 1 if self.isHD else 0
        tagString += self.newTagStringEntry("HD Video", hdValue)
        
        print self.fileTypes
        
        return tagString.strip()
    #end def tagString
#end class MovieMetadataParser
""""
<Video ratingKey="49" 
key="/library/metadata/49" 
guid="com.plexapp.agents.imdb://tt0499549?lang=en" 
studio="20th Century Fox" 
type="movie" 
title="Avatar" 
contentRating="PG-13" 
summary="In the future, Jake, a paraplegic war veteran, is brought to another planet, Pandora, which is inhabited by the Na&apos;vi, a humanoid race with their own language and culture. Those from Earth find themselves at odds with each other and the local culture." 
rating="7.4" 
viewOffset="796134" 
lastViewedAt="1308181195" 
year="2009" 
tagline="An All New World Awaits" 
thumb="/library/metadata/49/thumb?t=1302485153" 
art="/library/metadata/49/art?t=1302485153" duration="10260000" 
originallyAvailableAt="2009-12-10" 
addedAt="1283536330" 
updatedAt="1302485153">
<Media id="49" duration="9701000" bitrate="4678" aspectRatio="1.78" audioChannels="2" audioCodec="aac" videoCodec="h264" videoResolution="1080" container="mov" videoFrameRate="24p">
<Part id="49" key="/library/parts/49/Avatar%20(2009).m4v" duration="9701000" file="/Volumes/Drobo/Movies/Avatar (2009)/Avatar (2009).m4v" size="5810197410">
<Stream id="37843" streamType="1" codec="h264" index="0" language="?" languageCode="und" />
<Stream id="37844" streamType="2" selected="1" codec="aac" index="1" channels="2" language="English" languageCode="eng" />
<Stream id="37845" streamType="3" index="2" language="English" languageCode="eng" />
<Stream id="37846" streamType="3" index="3" language="?" languageCode="und" />
</Part>
</Media>
<Genre id="38547" tag="Science Fiction/Fantasy" />
<Genre id="43" tag="Animation" />
<Genre id="38549" tag="Historical" />
<Genre id="221" tag="Thriller" />
<Genre id="38548" tag="Action/Adventure" />
<Writer id="1037" tag="James Cameron" />
<Director id="1036" tag="James Cameron" />
<Role id="3407" tag="Sam Worthington" role="" thumb="http://ia.media-imdb.com/images/M/MV5BMTc5NTMyMjIwMV5BMl5BanBnXkFtZTcwNTMyNjYwMw@@._V1.jpg" />
<Role id="3408" tag="Zoe Saldana" role="" thumb="http://ia.media-imdb.com/images/M/MV5BODkzMzMwNjIxMl5BMl5BanBnXkFtZTcwODEyMDIzMQ@@._V1.jpg" />
<Role id="37427" tag="Stephen Lang (actor)" role="" />
<Role id="3409" tag="Stephen Lang" role="" thumb="http://ia.media-imdb.com/images/M/MV5BMTM3NzE4OTc2MF5BMl5BanBnXkFtZTcwNDE4OTE2MQ@@._V1.jpg" />
<Role id="3412" tag="Michelle Rodriguez" role="" thumb="http://ia.media-imdb.com/images/M/MV5BNDEzODQ1OTA0Nl5BMl5BanBnXkFtZTcwNjU2MDc1Mw@@._V1.jpg" />
<Role id="37428" tag="Joel David Moore" role="" />
<Role id="3411" tag="Giovanni Ribisi" role="" thumb="http://ia.media-imdb.com/images/M/MV5BMTk2MDAwMTQ5OV5BMl5BanBnXkFtZTcwNjY0MzY1Mw@@._V1.jpg" />
<Role id="1654" tag="Sigourney Weaver" role="" thumb="http://ia.media-imdb.com/images/M/MV5BMTk1MTcyNTE3OV5BMl5BanBnXkFtZTcwMTA0MTMyMw@@._V1.jpg" />
<Field name="art" locked="1" />
</Video>

"""