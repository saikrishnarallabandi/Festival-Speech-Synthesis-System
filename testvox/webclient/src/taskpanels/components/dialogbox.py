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
Shows a popup dialogbox (like window.alert)
"""

from pyjamas.ui.Button import Button
from pyjamas.ui.DialogBox import DialogBox
from pyjamas.ui.DockPanel import DockPanel
from pyjamas.ui.FlexTable import FlexTable
from pyjamas.ui.HTML import HTML
from pyjamas.ui.PopupPanel import PopupPanel
from pyjamas.ui.SimplePanel import SimplePanel

from pyjamas.ui import HasAlignment


class AlertDialogBox(DialogBox):
    def __init__(self, title, message):
        # Manually initialize DialogBox
        # Init section
        self.dragging = False
        self.dragStartX = 0
        self.dragStartY = 0
        self.child = None
        self.panel = FlexTable(
            Height="100%",
            BorderWidth="0",
            CellPadding="0",
            CellSpacing="0",
        )

        # Arguments section
        self.modal = True
        self.caption = HTML()
        self.panel.setWidget(0, 0, self.caption)
        self.caption.setStyleName("Caption")
        self.caption.addMouseListener(self)

        self.centered = True

        # End DialogBox.__init__

        cf = self.panel.getCellFormatter()
        rf = self.panel.getRowFormatter()

        rf.setStyleName(0, 'dialogTop')
        cf.setStyleName(0, 0, 'dialogTopLeft')
        cf.setStyleName(0, 1, 'dialogTopCenter')
        cf.setStyleName(0, 2, 'dialogTopRight')

        rf.setStyleName(1, 'dialogMiddle')
        cf.setStyleName(1, 0, 'dialogMiddleLeft')
        cf.setStyleName(1, 1, 'dialogMiddleCenter')
        cf.setStyleName(1, 2, 'dialogMiddleRight')

        rf.setStyleName(2, 'dialogBottom')
        cf.setStyleName(2, 0, 'dialogBottomLeft')
        cf.setStyleName(2, 1, 'dialogBottomCenter')
        cf.setStyleName(2, 2, 'dialogBottomRight')

        self.tli = SimplePanel()
        self.tli.setStyleName('dialogTopLeftInner')
        self.panel.setWidget(0, 0, self.tli)

        self.tci = SimplePanel()
        self.tci.setStyleName('dialogTopCenterInner')
        self.caption.setText(title)
        self.tci.add(self.caption)
        self.panel.setWidget(0, 1, self.tci)

        self.tri = SimplePanel()
        self.tri.setStyleName('dialogTopRightInner')
        self.panel.setWidget(0, 2, self.tri)

        self.mli = SimplePanel()
        self.mli.setStyleName('dialogMiddleLeftInner')
        self.panel.setWidget(1, 0, self.mli)

        closeButton = Button("Close", self)

        dock = DockPanel()
        dock.setSpacing(4)
        dock.add(closeButton, DockPanel.SOUTH)
        dock.add(HTML(message, True), DockPanel.NORTH)
        dock.setCellHorizontalAlignment(closeButton,
                                        HasAlignment.ALIGN_RIGHT)
        dock.setWidth("100%")
        self.mci = dock
        self.mci.setStyleName('dialogMiddleCenterInner')
        self.panel.setWidget(1, 1, self.mci)

        self.mri = SimplePanel()
        self.mri.setStyleName('dialogMiddleRightInner')
        self.panel.setWidget(1, 2, self.mri)

        self.bli = SimplePanel()
        self.bli.setStyleName('dialogBottomLeftInner')
        self.panel.setWidget(2, 0, self.bli)

        self.bci = SimplePanel()
        self.bci.setStyleName('dialogBottomCenterInner')
        self.panel.setWidget(2, 1, self.bci)

        self.bri = SimplePanel()
        self.bri.setStyleName('dialogBottomRightInner')
        self.panel.setWidget(2, 2, self.bri)

        # Finalize
        PopupPanel.__init__(self, None, True, glass=True,
                            StyleName='gwt-DialogBox')
        PopupPanel.setWidget(self, self.panel)

    def onClick(self, sender):
        self.hide()
