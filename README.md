#  Plex Media Tagger
Tested on Mac OS X 10.7 (Lion)

thanks goes to:
the [Plex team](http://www.plexapp.com), their PMS takes care of all the hard work of gathering the metadata and providing an intuitive web API to browse the local library.
the [Subler team](http://code.google.com/p/subler/), their CLI tool takes care of the actual embedding of the information.
the [AtomicParsley team](http://atomicparsley.sourceforge.net/), their CLI tool helps with the detection of previously tagged files.

## Installation:
Download the project: [Zip of project](https://github.com/ccjensen/PlexMediaTagger/zipball/master)

If you think you might want to tweak the code, clone the repository::

    git clone git://github.com/ccjensen/PlexMediaTagger.git

The tool requires python (pre-installed on most versions of Mac OS X and linux).

## Usage: 

		Usage: plexmediatagger.py [options]
		Example 1: plexmediatagger.py --tag
		Example 2: plexmediatagger.py -bq --tag --remove-all-tags --optimize -e subtitles -ip 192.168.0.2 --port 55400
		Example 3: plexmediatagger.py --subtitles -m 'D:\Movies' '/Volumes/Media/Movies' -m '\' '/'

The tool uses the comment metadata field to store metadata that does not have its own tag, but is a value that iTunes stores in its internal database (such as rating and playcount). There is an iTunes script in the extra's folder that can load this information into iTunes. So after the tools has run and embedded the information, select the corresponding file in iTunes and run the script. This will load in that extra information that cannot be embedded.

Note: Filepaths to media items in PMS need to be the same as on machine that is running this script (can be worked around by using the -m option to modify the file path).

### Options:
Options:  
 `-h, --help`          show this help message and exit  
 `-t, --tag`           tag all compatible file types, and update any  
                       previously tagged files (if metadata in plex has  
                       changed)  
 `-r, --remove-tags`   remove all compatible tags from the files  
 `-f, --force`         ignore previous work and steam ahead with task (will  
                       re-tag previously tagged files, etc.)  
 `-o, --optimize`      interleave the audio and video samples, and put the  
                       "MooV" atom at the beginning of the file  
 `--subtitles`         export any subtitles to the same path as the video  
                       file  
 `--coverart`          export the coverart to the same path as the video file  
 `-m <find> <replace>` perform a find & replace operation on the pms' media  
                       file paths (useful if you are running the script on a  
                       different machine than the one who is hosting the pms,  
                       i.e. the mount paths are different). Supply multiple  
                       times to perform several different replacements  
                       (operations are performed in order supplied).  
 `-i IP, --ip=IP`      specify an alternate IP address that hosts a PMS to  
                       connect to (default is localhost)  
 `-p PORT, --port=PORT`specify an alternate port number to use when  
                       connecting to the PMS (default is 32400)  
 `-b, --batch`         disable interactive mode. Requires no human  
                       intervention once launched, and will perform  
                       operations on all valid files  
 `--interactive`       interactivly select files to operate on [default]  
 `-v, --verbose`       increase verbosity (can be supplied 0-2 times)  
 `-q, --quiet`         ninja-like processing (can only be used when in batch  
                       mode)  
 `-d, --dry-run`       pretend to do the job, but never actually change or  
                       export anything. Pretends that all tasks succeed.  
                       Useful for testing purposes  