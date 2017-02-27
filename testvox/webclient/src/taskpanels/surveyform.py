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

from pyjamas.ui.Button import Button
from pyjamas.ui.Grid import Grid
from pyjamas.ui.HTML import HTML
from pyjamas.ui.FlowPanel import FlowPanel
from pyjamas.ui.SimplePanel import SimplePanel

from components.selectquestion import SelectQuestion
from components.radioquestion import RadioQuestion
from components.textquestion import TextQuestion
from components.dialogbox import AlertDialogBox

from common_utils import log


class SurveyForm(FlowPanel):
    """Displays a questionnaire typically used for entry/exit surveys"""

    def __init__(self, task_info, testvox_service, main_handler):
        FlowPanel.__init__(self)
        self.task_info = task_info
        self.testvox_service = testvox_service
        self.main_handler = main_handler

        self.is_preview = task_info['is_preview']
        self.empty_allowed = self.is_preview

        self.build_panel()

    def build_panel(self):
        """Generates the survey form and creates a submit button"""
        info = self.task_info

        self.instruction_holder = SimplePanel()
        self.instruction_holder.setID('task_instruction')
        instruction = info['instruction']
        if self.is_preview:
            instruction = ''.join(['<div class="alert">',
                                   'Task Not Accepted. Preview Enabled.',
                                   '</div>',
                                   instruction])
        self.instruction = HTML(instruction)
        self.instruction_holder.add(self.instruction)
        self.add(self.instruction_holder)

        self.questions_grid = Grid(rows=len(info['questions']),
                                   columns=2)
        self.questions_grid.addStyleName('narrowtable')

        self.add(self.questions_grid)

        self.questions = []
        count = 0
        for q in info['questions']:
            question = None
            try:
                q_name = q['name']
                q_text = q['text']
                q_type = q['type']
            except KeyError:
                log.error("Questions must have 'name' and 'text' and 'type'")
                # Skip incorrect question
                continue
            if q_type in ['select', 'radio', 'check']:
                try:
                    q_options = q['options']
                except KeyError:
                    log.error("Missing 'options' for %s question" % q_type)

            if q_type == 'select':
                question = SelectQuestion(q_name, q_options,
                                          'horizontal',
                                          empty_allowed=self.empty_allowed)
            elif q_type == 'radio':
                question = RadioQuestion(q_name, 'radio', q_options,
                                         'horizontal',
                                         empty_allowed=self.empty_allowed)
            elif q_type == 'check':
                question = RadioQuestion(q_name, 'check', q_options,
                                         'horizontal',
                                         empty_allowed=self.empty_allowed)
            elif q_type == 'text':
                question = TextQuestion(q_name, 'horizontal',
                                        empty_allowed=self.empty_allowed)
            if question is not None:
                self.questions.append(question)
                self.questions_grid.setText(count, 0, q_text)
                self.questions_grid.setWidget(count, 1, question.get_widget())
                self.questions_grid.cellFormatter.addStyleName(
                    count, 0, 'bottombordered')
                self.questions_grid.cellFormatter.addStyleName(
                    count, 1, 'bottombordered')

                count += 1

        self.submit_button = Button("Submit", getattr(self,
                                                      'onSubmitButtonClick'))
        self.add(HTML("<br />"))
        self.add(self.submit_button)

    def onSubmitButtonClick(self, sender):
        answers = []
        for q in self.questions:
            answer = q.get_answer()
            if answer is None:
                dbox = AlertDialogBox('Oops',
                                      'You must answer all questions')
                dbox.show()
                return
            answers.append(answer)
        log.info(answers)

        self.testvox_service.get_next_task(
            {self.task_info['name']: answers},
             self.main_handler)
