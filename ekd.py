# -*- coding: utf-8 -*-

'''
-----------------------------------------------------------------------
GPL v3
-----------------------------------------------------------------------
EKD can be used to make post production operations for video files and images.
Copyright (C) 2008 Lama Angelo (the historical developer of the
program) with the contribution of Aurélien Cedeyn and Olivier Ponchaut to
this 2010 version of EKD.

EKD is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your
option) any later version.

EKD is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see http://www.gnu.org/licenses
or write to the Free Software Foundation,Inc., 51 Franklin Street,
Fifth Floor, Boston, MA 02110-1301  USA

To contact the developpers of EKD, go here:
http://ekd.tuxfamily.org/forum/forumdisplay.php?fid=8
-----------------------------------------------------------------------
'''

"""
    This program launch Ekd with the command line
"""

# Version de ekd
__version__ = "2.0.8"

import getopt, sys
from moteur_modules_animation.mencoder import Mencoder
from PyQt4.QtCore import QCoreApplication, SIGNAL
###############
from moteur_modules_common.EkdCompatiblePython2Et3 import EkdPrint
###############

def usage( long = False ):
    #print "Usage : %s [-h] inputfile [-c codec] [-o outputfile]" % (sys.argv[0])
    EkdPrint(u"Usage : %s [-h] inputfile [-c codec] [-o outputfile]" % (sys.argv[0])
    '''
    print "      inputfile : file to work\n" \
        "      -h\n" \
        "      --help : This message\n" \
        "      -c codec\n" \
        "      --codec codec : perform codec on inputfile\n" \
        "      -o outputfile\n" \
        "      --outputfile : output result to file"
    '''
    EkdPrint(u"      inputfile : file to work\n" \
        u"      -h\n" \
        u"      --help : This message\n" \
        u"      -c codec\n" \
        u"      --codec codec : perform codec on inputfile\n" \
        u"      -o outputfile\n" \
        u"      --outputfile : output result to file")
    if long :
	'''
        print " CODECS AVAILABLE :\n" \
            "  (mencoder)\n" \
            '  * copie : copy the inputfile to output\n',\
            '  * avirawsanscompression : raw avi encoding\n',\
            '  * codecdivx4 : divx4 encoding\n',\
            '  * codecmotionjpeg : motion JPEG encoding\n',\
            '  * codecmpeg1 : mpeg1 encoding\n',\
            '  * codecmpeg2 : mpeg2 encoding\n',\
            '  * codecwmv2 : WMV enconding\n',\
            '  * codecxvid : XVID encoding\n',\
            '  * macromediaflashvideo : Flash encoding\n',\
            '  * codech264mpeg4_ext_h264 : MPEG4 .h264 encoding\n',\
            '  * youtube_16/9_HQ : Youtube 16/9 HQ encoding\n',\
            '  * youtube_16/9_MQ : Youtube 16/9 MQ encoding\n',\
            '  * youtube_16/9_LQ : Youtube 16/9 LQ encoding\n',\
            '  * youtube_4/3_HQ : Youtube 4/3 HQ encoding\n',\
            '  * youtube_4/3_MQ : Youtube 4/3 MQ encoding\n',\
            '  * youtube_4/3_LQ : Youtube 4/3 LQ encoding\n',\
            '  * google_video_16/9_HQ : Google video 16/9 HQ encoding\n',\
            '  * google_video_16/9_MQ : Google video 16/9 MQ encoding\n',\
            '  * google_video_16/9_LQ : Google video 16/9 LQ encoding\n',\
            '  * google_video_4/3_HQ : Google video 4/3 HQ encoding\n',\
            '  * google_video_4/3_MQ : Google video 4/3 MQ encoding\n',\
            '  * google_video_4/3_LQ : Google video 4/3 LQ encoding\n',\
            '  * dailymotion_sd_4/3 : Daily Motion 4/3 encoding\n',\
            '  * dailymotion_sd_16/9 : Daily Motion video 16/9 encoding\n',\
            '  * dailymotion_HD720p : Daily Motion 720px HD encoding\n',\
            '  * niveaudegris : grayscale input video\n',\
            '  * placesoustitres : add subtitle\n',\
            '  * miroir : mirror input video\n',\
            '  * changement_resolution : change resolution\n',\
            '  * tournervideo : rotate video\n',\
            '  * desentrelacer : desinterlace video\n',\
            '  * extractionvideo : extract from video\n',\
            '  * fusion_video : merge video\n',\
            '  * fusion_audio_et_video_1 : merge audio with sound\n',\
            '  * fusion_audio_et_video_2 : merge audio with sound\n',\
            '  * codech264mpeg4 : H264 mpeg4 encoding\n',\
            '  * codech264mpeg4_nosound : H264 mpeg4 without sound\n',\
            '  * luminositecontraste : Change brightness/contrast\n',\
            '  * decoupervideo : Cut video border\n',\
            '  * couleursaturationhue : \n',\
            '  * decoupervideo_nosound : Split video without sound\n',\
            '  * flouboitebloxblur : Blur video\n',\
            '  * bruit : Noise video\n',\
            '  * decoupagelibre : Free crop'
	'''
	EkdPrint(u" CODECS AVAILABLE :\n" \ 
            u"  (mencoder)\n" \ 
            u'  * copie : copy the inputfile to output\n' \ +
            u'  * avirawsanscompression : raw avi encoding\n' \ +
            u'  * codecdivx4 : divx4 encoding\n' \ +
            u'  * codecmotionjpeg : motion JPEG encoding\n' \ +
            u'  * codecmpeg1 : mpeg1 encoding\n' \ +
            u'  * codecmpeg2 : mpeg2 encoding\n' \ +
            u'  * codecwmv2 : WMV enconding\n' \ +
            u'  * codecxvid : XVID encoding\n' \ +
            u'  * macromediaflashvideo : Flash encoding\n' \ +
            u'  * codech264mpeg4_ext_h264 : MPEG4 .h264 encoding\n' \ +
            u'  * youtube_16/9_HQ : Youtube 16/9 HQ encoding\n' \ +
            u'  * youtube_16/9_MQ : Youtube 16/9 MQ encoding\n' \ +
            u'  * youtube_16/9_LQ : Youtube 16/9 LQ encoding\n' \ +
            u'  * youtube_4/3_HQ : Youtube 4/3 HQ encoding\n' \ +
            u'  * youtube_4/3_MQ : Youtube 4/3 MQ encoding\n' \ +
            u'  * youtube_4/3_LQ : Youtube 4/3 LQ encoding\n' \ +
            u'  * google_video_16/9_HQ : Google video 16/9 HQ encoding\n' \ +
            u'  * google_video_16/9_MQ : Google video 16/9 MQ encoding\n' \ +
            u'  * google_video_16/9_LQ : Google video 16/9 LQ encoding\n' \ +
            u'  * google_video_4/3_HQ : Google video 4/3 HQ encoding\n' \ +
            u'  * google_video_4/3_MQ : Google video 4/3 MQ encoding\n' \ +
            u'  * google_video_4/3_LQ : Google video 4/3 LQ encoding\n' \ +
            u'  * dailymotion_sd_4/3 : Daily Motion 4/3 encoding\n' \ +
            u'  * dailymotion_sd_16/9 : Daily Motion video 16/9 encoding\n' \ +
            u'  * dailymotion_HD720p : Daily Motion 720px HD encoding\n' \ +
            u'  * niveaudegris : grayscale input video\n' \ +
            u'  * placesoustitres : add subtitle\n' \ +
            u'  * miroir : mirror input video\n' \ +
            u'  * changement_resolution : change resolution\n' \ +
            u'  * tournervideo : rotate video\n' \ +
            u'  * desentrelacer : desinterlace video\n' \ +
            u'  * extractionvideo : extract from video\n' \ +
            u'  * fusion_video : merge video\n' \ +
            u'  * fusion_audio_et_video_1 : merge audio with sound\n' \ +
            u'  * fusion_audio_et_video_2 : merge audio with sound\n' \ +
            u'  * codech264mpeg4 : H264 mpeg4 encoding\n' \ +
            u'  * codech264mpeg4_nosound : H264 mpeg4 without sound\n' \ +
            u'  * luminositecontraste : Change brightness/contrast\n' \ +
            u'  * decoupervideo : Cut video border\n' \ +
            u'  * couleursaturationhue : \n' \ +
            u'  * decoupervideo_nosound : Split video without sound\n' \ +
            u'  * flouboitebloxblur : Blur video\n' \ +
            u'  * bruit : Noise video\n' \ +
            u'  * decoupagelibre : Free crop')
    sys.exit(2)

def progress(value):
    #print "%s %\r" % value,
    EkdPrint("%s %\r" % value,)

if __name__ == "__main__":
    codec = False
    outputfile = False

    application = QCoreApplication(sys.argv)

    try :
        if len(sys.argv) < 2 :
            raise getopt.GetoptError("Not enought arguments")
        optlist, inputfiles = getopt.gnu_getopt(
                                sys.argv[1:],
                                "hc:o:",
                                [ "help" , "codec:", "outputfile:"]
                        )
    except getopt.GetoptError, err:
        #print >> sys.stderr, str(err)
        EkdPrint(>> sys.stderr + str(err))
        usage()

    for option, value in optlist:
        if option in ("-c", "--codec") :
            codec = value
        elif option in ("-o", "--output") :
            outputfile = value
        elif option in ("-h", "--help"):
            usage(long = True)
        else:
            usage()
    '''
    print "Debug : Option parsing ok - " \
            "codec %s - input %s - output %s -" \
            % (codec, inputfiles, outputfile)
    '''
    EkdPrint(u"Debug : Option parsing ok - " \
            u"codec %s - input %s - output %s -" \
            % (codec, inputfiles, outputfile))

    mencoder_codecs = [
        'copie',
        'avirawsanscompression',
        'codecdivx4',
        'codecmotionjpeg',
        'codecmpeg1',
        'codecmpeg2',
        'codecwmv2',
        'codecxvid',
        'macromediaflashvideo',
        'codech264mpeg4_ext_h264',
        'youtube_16/9_HQ',
        'youtube_16/9_MQ',
        'youtube_16/9_LQ',
        'youtube_4/3_HQ',
        'youtube_4/3_MQ',
        'youtube_4/3_LQ',
        'google_video_16/9_HQ',
        'google_video_16/9_MQ',
        'google_video_16/9_LQ',
        'google_video_4/3_HQ',
        'google_video_4/3_MQ',
        'google_video_4/3_LQ',
        'dailymotion_sd_4/3',
        'dailymotion_sd_16/9',
        'dailymotion_HD720p',
        'niveaudegris',
        'placesoustitres',
        'miroir',
        'changement_resolution',
        'tournervideo',
        'desentrelacer',
        'extractionvideo',
        'fusion_video',
        'fusion_audio_et_video_1',
        'fusion_audio_et_video_2',
        'codech264mpeg4',
        'codech264mpeg4_nosound',
        'luminositecontraste',
        'decoupervideo',
        'couleursaturationhue',
        'decoupervideo_nosound',
        'flouboitebloxblur',
        'bruit',
        'decoupagelibre'
        ]

    if codec in mencoder_codecs:
        process = Mencoder(inputfiles[0], outputfile, codec)
        process.setCommand(2)
        process.connect(process, SIGNAL("progress(int)"), progress)
        process.connect(process, SIGNAL("finished(int)"), application.quit)
        process.start()
        process.wait(0)
    else :
        usage()

    sys.exit(application.exec_())
