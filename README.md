#  Plex Media Tagger
Tested on Mac OS X 10.6 (Snow Leopard)

thanks goes to:
the [Subler team](http://code.google.com/p/subler/), their CLI tool takes care of the actual embedding of the information.
the [Plex team](http://www.plexapp.com), their PMS takes care of all the hard work of gathering the metadata and providing an intuitive web API to browse the local library.

## Installation:
Retrieve the tool and its support files with:

    git clone git://github.com/ccjensen/PlexMediaTagger.git

The tool requires python (pre-installed on Snow Leopard) and a python module called lxml. lxml was successfully installed on my system using:
    
    sudo env ARCHFLAGS="-arch i386 -arch x86_64" easy_install lxml

## Usage: 

    Usage: plexmediatagger.py [options] [alternate IP/Domain (default is localhost)] [port number (default is 32400)]
    Example: plexmediatagger.py -of 192.168.0.2 55400
    
Note: Filepaths to media items in PMS need to be the same as on machine that is running this script.

### Options:
  -h, --help           show this help message and exit
  -b, --batch          Disables interactive. Requires no human intervention
                       once launched, and will perform operations on all files
  -i, --interactive    interactively select files to operate on [default]
  -o, --optimize       Interleaves the audio and video samples, and puts the
                       "MooV" atom at the begining of the file. [default]
  -v, --verbose        Increase verbosity
  -q, --quiet          For ninja-like processing (Can only be used when in
                       batch mode)
  -f, --force-tagging  Tags all chosen files, even previously tagged ones

