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
##  Date  : July 2012                ##
###########################################################################
"""
Implements a radiobutton / checkbox type question
"""

from pyjamas.ui.RadioButton import RadioButton
from pyjamas.ui.CheckBox import CheckBox
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.VerticalPanel import VerticalPanel

from base import Question


class RadioQuestion(Question):
    def __init__(self, name, select_type, options,
                 layout='horizontal',
                 empty_allowed=False):
        Question.__init__(self, name, layout,
                          empty_allowed=empty_allowed)

        self.select_type = select_type
        self.options = options

        self.button_list = []
        if self.select_type == 'radio':
            self.button_list = [RadioButton("name_%s"%name, x) for x in self.options]
        else:
            self.button_list = [CheckBox(x) for x in self.options]

        if layout == 'horizontal':
            self.widget = HorizontalPanel()
        else:
            self.widget = VerticalPanel()

        for button in self.button_list:
            self.widget.add(button)

    def get_answer(self):
        values = []
        for button in self.button_list:
            if button.isChecked():
                values.append(button.getText())

        if not values:
            if not self.empty_allowed:
                return None

        # Return a single item for radio button, and a list of items
        # for checkbox
        if self.select_type == 'radio':
            return {'name': self.name,
                    'response': values[0]}
        else:
            return {'name': self.name,
                    'response': values}
