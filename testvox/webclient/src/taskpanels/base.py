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
"""Displays a questionnaire typically used for entry/exit surveys"""

from pyjamas.ui.HTML import HTML
from pyjamas.ui.SimplePanel import SimplePanel
from pyjamas.ui.VerticalPanel import VerticalPanel

from common_utils import log

from components.dialogbox import AlertDialogBox


class BaseListeningTask(VerticalPanel):
    """Displays a listening task"""

    def __init__(self, task_info, testvox_service, main_handler):
        VerticalPanel.__init__(self)
        self.task_info = task_info
        self.testvox_service = testvox_service
        self.main_handler = main_handler

        self.is_preview = self.task_info['is_preview']

        self.task_input_panel = None
        self.continue_button = None
        self.current_item = -1

        self.task_answers = []

        self.continue_button_base_label = "Continue"
        if self.is_preview:
            self.continue_button_base_label = "Continue PREVIEW"

        self.instruction_holder = SimplePanel()
        self.instruction_holder.setID('task_instruction')
        instruction = task_info['instruction']
        if self.is_preview:
            instruction = ''.join(['<div class="alert">',
                                   'Task Not Accepted. Preview Enabled.',
                                   '</div>',
                                   instruction])
        self.instruction = HTML(instruction)
        self.instruction_holder.add(self.instruction)
        self.add(self.instruction_holder)

    def show_next_item(self):
        """Displays listening task for the next item in line. Stores
        results for the current item if any

        """

        if self.current_item >= 0:
            try:
                answer = self._get_current_answer()
                if answer is None and not self.is_preview:
                    dbox = AlertDialogBox(
                        'Err..',
                        'Please do this task before continuing.')
                    dbox.show()

                    return
                else:
                    self.task_answers.append(answer)
            except Exception as e:
                log.error("Error in showing next task: " + str(e))

        if self.current_item >= len(self.task_info['data']) - 1:
            # All done. Submit results
            self.testvox_service.get_next_task(
                {self.task_info['name']: self.task_answers}, self.main_handler)
        else:
            # Another item can be shown
            self.current_item += 1
            self._show_item(self.current_item)

    def _build_panel(self):
        """Add necessary components to panel for the listening test"""
        raise NotImplementedError

    def _get_current_answer(self):
        """Gets the currently filled input on the web form. This is
        the response to the listening test.

        """
        raise NotImplementedError

    def _show_item(self, item_number):
        """Modify the set of widgets to display current item in the
        listening test

        """
        raise NotImplementedError

    def onContinueButtonClick(self, sender):
        """Action to do when continue button is clicked"""
        raise NotImplementedError

    def _clear_panel(self):
        """Removes all added widgets"""
        raise NotImplementedError
