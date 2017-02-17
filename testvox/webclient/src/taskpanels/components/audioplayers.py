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
Implements functionality to use NiftyPlayer, JPlayer, etc.
"""

from __pyjamas__ import JS, wnd

from common_utils import log


class NiftyPlayer():
    def __init__(self, player_id, autoplay):
        self.player_id = player_id
        self.autoplay = autoplay

        self.flashtext = """
        <object type="application/x-shockwave-flash"
        data="/static/niftyplayer/niftyplayer.swf"
        width="165" height="38" id="%(player_id)s">
        <param name=movie value="niftyplayer.swf">
        <param name=quality value=high>
        <param name=bgcolor value=#FFFFFF>""" % {'player_id': player_id}

    def get_html(self):
        return self.flashtext

    def js_player(self):
        playerid = self.player_id
        return JS(""" new $wnd.niftyplayer(@{{playerid}})""")

    def is_ready(self):
        try:
            self.js_player().getState()
            return True
        except:
            return False

    def play(self, url=None):
        """Sets the URL of the flash object to be the required URL"""
        player = self.js_player()
        if self.autoplay:
            player.loadAndPlay(url)
        else:
            player.load(url)

    def stop(self):
        self.js_player().stop()
