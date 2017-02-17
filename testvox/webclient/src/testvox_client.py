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
"""
Main View for displaying tasks through the webclient.

This sets up the DOM root and creates a panel based on
data about the task as received from JSON query.
"""

from pyjamas.ui.CSS import StyleSheetCssFile
from pyjamas.ui.HTML import HTML
from pyjamas.ui.Image import Image
from pyjamas.ui.FlowPanel import FlowPanel
from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.SimplePanel import SimplePanel
from pyjamas import Window
from common_utils import log, testvox_service

StyleSheetCssFile('/static/css/testvox/testvox.css')


class TestVoxMainPanel(FlowPanel):
    """Sets up the main document within which individual panels for
    tasks will be adde
    """

    def __init__(self):
        FlowPanel.__init__(self)

        self.setID('page-container')

        # Add header
        # <div id="header-container">
        #   <div id="header" class="wrapper clearfix">
        #     LOGO and TITLE
        self.header_container = SimplePanel()
        self.header_container.setID('header-container')
        self.header = FlowPanel()
        self.header.setID('header')
        self.header.addStyleName('wrapper')
        self.header.addStyleName('clearfix')
        self.logo = Image()
        self.logo.setID('header-logo')
        self.header.add(self.logo)
        self.pagetitle = HTML('')
        self.pagetitle.setID('title')
        self.header.add(self.pagetitle)
        self.header_container.add(self.header)

        self.add(self.header_container)

        # Create a placeholder for Messages to the user
        self.top_message_block = HTML("<b>Loading...</b>")
        self.add(self.top_message_block)

        # Ask the service for data about current task
        testvox_service.get_next_task({}, self)

    def onRemoteError(self, code, errobj, request_info):
        """Callback for error received from JSON Service"""
        log.error(errobj)
        self.top_message_block.setHTML(' '.join(
            ["<b>Error:</b>",
             "Task could not be loaded"]))

    def onRemoteResponse(self, response, request_info):
        """Callback for completed JSON method"""
        log.info(request_info)
        if request_info.method == 'get_next_task':
            self.clear_main_panel()
            self.initialize_main_panel(response)
        else:
            pass

    def initialize_main_panel(self, task_info):
        """Build the main panel based on task data as received from
        JSON query.

        """
        try:
            is_amt_preview = task_info['is_amt_preview']
        except KeyError:
            is_amt_preview = False
        if is_amt_preview:
            instruction = 'Note: You have not accepted this HIT.'
        else:
            instruction = ''

        self.top_message_block.setHTML(instruction)

        # Set the Title
        try:
            pagetitle = task_info['testvox_config']['pagetitle']
        except:
            # Use default title
            pagetitle = 'TestVox'
            pass
        self.pagetitle.setHTML('<h1>%s</h1>' % pagetitle)

        # Set the Logo
        try:
            logo_url = task_info['testvox_config']['logo_url']
        except:
            logo_url = '/static/images/testvox_logo.png'
        self.logo.setUrl(logo_url)
        self.task_panel = SimplePanel()
        self.task_panel.setID('main')
        self.task_panel.addStyleName('wrapper')
        self.task_panel.addStyleName('clearfix')
        task_type = task_info['task_type']
        if task_type == 'surveyform':
            from taskpanels.surveyform import SurveyForm
            self.task_panel.add(SurveyForm(task_info, testvox_service, self))
        elif task_type == 'transcriptiontask':
            from taskpanels.transcriptiontask import TranscriptionListeningTask
            self.task_panel.add(
                TranscriptionListeningTask(task_info,
                                           testvox_service, self))
        elif task_type == 'abtask':
            from taskpanels.abtask import ABListeningTask
            self.task_panel.add(
                ABListeningTask(task_info,
                                testvox_service, self))
        elif task_type == 'radiotask':
            from taskpanels.radiotask import RadioListeningTask
            self.task_panel.add(
                RadioListeningTask(task_info,
                                   testvox_service, self, mode='radio'))
        elif task_type == 'checktask':
            from taskpanels.radiotask import RadioListeningTask
            self.task_panel.add(
                RadioListeningTask(task_info,
                                   testvox_service, self, mode='check'))
        elif task_type == 'wordchoicetask':
            from taskpanels.wordchoicetask import WordChoiceListeningTask
            self.task_panel.add(
                WordChoiceListeningTask(task_info,
                                   testvox_service, self))
        elif task_type == 'finished':
            if task_info['submit_url']:
                Window.setLocation(task_info['submit_url'])
            else:
                from taskpanels.finished import Finished
                self.task_panel.add(Finished(task_info))
        else:
            log.error("Attempt to display invalid task type: %s" % task_type)
            self.top_message_block.setHTML(''.join([
                "<b>Error:</b>",
                "Could not load the task specified"]))
            return
        self.add(self.task_panel)

    def clear_main_panel(self):
        self.top_message_block.setHTML('')
        try:
            self.remove(self.task_panel)
        except AttributeError:
            pass

if __name__ == '__main__':
    RootPanel().add(TestVoxMainPanel())
