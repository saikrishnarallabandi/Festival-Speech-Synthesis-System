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
##  Date  : July 2012                                                    ##
###########################################################################
"""Displays a transcription listening task. Shows media clip and asks for
text input

"""
import random

from base import BaseListeningTask
from components.mediaplayer import MediaPlayer

from pyjamas.ui.Button import Button
from pyjamas.ui.Label import Label
from pyjamas.ui.TextArea import TextArea

from common_utils import log


class TranscriptionListeningTask(BaseListeningTask):
    """Displays a Transcription Task"""
    def __init__(self, task_info, testvox_service, main_handler):
        BaseListeningTask.__init__(self, task_info,
                                   testvox_service, main_handler)
        self.data = self.task_info['data']
        self.data_randomize = self.task_info['data_randomize']

        self._build_panel()

    def _build_panel(self):
        # Ensure that there are more than 0 items to transcribe
        if not self.data:
            log.error("No media items to display.")
            self.instruction.setHTML("Could not load task. Sorry!")
            return

        # Shuffle the order in which media is played
        if self.data_randomize:
            random.shuffle(self.data)

        # Add progressbar
        self.progress_label = Label("Clip %3d of %5d     :" % (1,
                                                               len(self.data)))
        self.add(self.progress_label)

        # Add the Media Player
        self.mediaplayer = MediaPlayer(self.task_info)
        self.add(self.mediaplayer)

        # Add the textarea for input
        self.textarea = TextArea()
        self.textarea.setVisibleLines(10)
        self.textarea.setWidth(500)
        self.add(self.textarea)

        # Add continue button
        self.continue_button = Button(
            self.continue_button_base_label,
            getattr(self, 'onContinueButtonClick'))
        self.add(self.continue_button)

        # Show the next available item now!
        self.show_next_item()

    def _get_current_answer(self):
        try:
            item_name = self.data[self.current_item]['name']
        except KeyError:
            item_name = self.data[self.current_item]['filename']
        answer = self.textarea.getText().strip()
        if not answer:
            return None
        return {'data_name': item_name,
                'data_response': answer,
                'data_extra_info': {}}

    def _show_item(self, item_number):
        log.info("Showing item %d" % item_number)
        total_item_count = len(self.data)
        self.progress_label.setText("Clip %3d of %5d     :" % (
            item_number + 1, total_item_count))
        self.mediaplayer.play(self.data[item_number]['filename'])

        self.textarea.setText('')

        if item_number == total_item_count - 1:
            # Last task
            self.continue_button.setText("Finish")
            if self.is_preview:
                self.continue_button.setText("Finish PREVIEW")
        else:
            # More tasks
            self.continue_button.setText(' '.join([
                self.continue_button_base_label,
                'to clip %3d of %5d' % (item_number + 2, total_item_count)]))

    def onContinueButtonClick(self, sender):
        self.mediaplayer.stop()
        self.show_next_item()

    def _clear_panel(self):
        self.remove(self.progress_label)
        self.remove(self.mediaplayer)
        self.remove(self.textarea)
        self.remove(self.continue_button)
