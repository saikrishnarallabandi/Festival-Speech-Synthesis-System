###########################################################################
##                                                                       ##
##                  Language Technologies Institute                      ##
##                     Carnegie Mellon University                        ##
##                         Copyright (c) 2012                            ##
##                        All Rights Reserved.                           ##
##                                                                       ##
##  Permission is hereby granted, free of charge, to use and distribute  ##
##  this software and its documentation without restriction, including   ##
##  without limitation the rights to use, copy, modify, merge, publish,  ##
##  distribute, sublicense, and/or sell copies of this work, and to      ##
##  permit persons to whom this work is furnished to do so, subject to   ##
##  the following conditions:                                            ##
##   1. The code must retain the above copyright notice, this list of    ##
##      conditions and the following disclaimer.                         ##
##   2. Any modifications must be clearly marked as such.                ##
##   3. Original authors' names are not deleted.                         ##
##   4. The authors' names are not used to endorse or promote products   ##
##      derived from this software without specific prior written        ##
##      permission.                                                      ##
##                                                                       ##
##  CARNEGIE MELLON UNIVERSITY AND THE CONTRIBUTORS TO THIS WORK         ##
##  DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING      ##
##  ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT   ##
##  SHALL CARNEGIE MELLON UNIVERSITY NOR THE CONTRIBUTORS BE LIABLE      ##
##  FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES    ##
##  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN   ##
##  AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,          ##
##  ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF       ##
##  THIS SOFTWARE.                                                       ##
##                                                                       ##
###########################################################################
##                                                                       ##
##  Author: Alok Parlikar (aup@cs.cmu.edu)                               ##
##  Date  : June 2013                                                    ##
###########################################################################
"""
Implements functionality to use NiftyPlayer
"""

from __pyjamas__ import JS, wnd

from pyjamas.ui.HTML import HTML
from pyjamas.ui.SimplePanel import SimplePanel
from pyjamas.Timer import Timer

from common_utils import log
import audioplayers


class MediaPlayer(SimplePanel):
    """Provides interaction with a mediaplayer
    """
    playercount = 0

    def __init__(self, task_info):
        SimplePanel.__init__(self)
        self.task_info = task_info

        # Detect which type of mediaplayer is desired
        try:
            player_type = task_info['media_player_type']
        except KeyError:
            player_type = 'niftyplayer'

        log.info('Desired media player is %s' % player_type)

        # Import the appropriate mediaplayer
        player_class_mapping = {
            'niftyplayer': audioplayers.NiftyPlayer,
        }

        self.DesiredPlayer = player_class_mapping[player_type]

        self.player_id = player_type + str(MediaPlayer.playercount)
        MediaPlayer.playercount += 1

        try:
            self.autoplay = self.task_info['audio_autoplay']
        except:
            self.autoplay = False

        self.player = self.DesiredPlayer(self.player_id, self.autoplay)

        self.add(HTML(self.player.get_html()))
        self.ready = False
        self.__cachedURL = None
        Timer(500, self)

    def wait_for_player(self):
        """Wait for player to be loaded. Polls with a timer"""

        if self.player.is_ready():
            self.ready = True
            log.info('Mediaplayer is now ready')
            if self.__cachedURL is not None:
                self.play(self.__cachedURL)
                self.__cachedURL = None
            return
        else:
            log.info('Waiting for Mediaplayer to load...')
            Timer(500, self)

    def onTimer(self, event):
        self.wait_for_player()

    def play(self, url=None):
        """Plays the given URL"""

        if not self.ready:
            self.__cachedURL = url
            log.warning('Audio player not yet ready')
            return
        else:
            url = '/media/%s/%s' % (self.task_info['exp_id'], url)
            log.info("player %s: %s" % (self.player_id, url))
            self.player.play(url)

    def stop(self):
        self.player.stop()
