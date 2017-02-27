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
Detects runtime Environment. Useful for debugging and compatibility
with Google App Engine
"""

import os
import sys

from os import environ

IS_GAE = False
IS_DEBUG = False

LOCAL_PORT = 8080
LOCAL_IP = '127.0.0.1'

OUTPUT_DIR = None

DATA_DIR = None
LOG_DIR = None
SESSIONS_DIR = None

_server_software = None
try:
    _server_software = environ['SERVER_SOFTWARE']
except:
    pass

if _server_software is not None:
    if _server_software.startswith('Development'):
        IS_GAE = True
        IS_DEBUG = True

    if _server_software.startswith('Google'):
        IS_GAE = True
        IS_DEBUG = False

if not IS_GAE:
    from os import path
    OUTPUT_DIR = path.join(path.dirname(path.abspath(__file__)), 'gen')

    DATA_DIR = path.join(OUTPUT_DIR, 'data')
    LOG_DIR = path.join(OUTPUT_DIR, 'log')
    SESSIONS_DIR = path.join(OUTPUT_DIR, 'sessions')

    for dirname in [OUTPUT_DIR, DATA_DIR, LOG_DIR, SESSIONS_DIR]:
        # Make sure the directory exists
        try:
            os.mkdir(dirname)
        except OSError:
            # Already exists
            pass

    if len(sys.argv) > 0:
        try:
            import argparse

            parser = argparse.ArgumentParser(
                description='Start TestVox webserver')

            parser.add_argument('-d', '--debug', action='store_true',
                                help='Run server in Debug mode')

            parser.add_argument('-p', '--port', metavar='NUM', type=int,
                                default=8080, required=False,
                                help='Listen on port NUM. Default: 8080')

            parser.add_argument('-i', '--ip', metavar='A.B.C.D', type=str,
                                default='127.0.0.1', required=False,
                                help='Bind to interface A.B.C.D.')

            args = parser.parse_args()
        except ImportError:
            # Python 2.6 doesn't have argparse
            # But optparse is deprecated in 2.7
            from optparse import OptionParser
            parser = OptionParser()
            parser.add_option('-d', '--debug', dest='debug',
                              action='store_true',
                              help='Run server in Debug mode')
            parser.add_option('-p', '--port', dest='port',
                              metavar='NUM', type=int,
                              default=8080,
                              help='Listen on port NUM. Default: 8080')
            parser.add_option('-i', '--ip', dest='ip',
                              metavar='A.B.C.D', type=str,
                              default='127.0.0.1',
                              help='Bind to interface A.B.C.D')

            options, args = parser.parse_args()
            # We actually want options to be called args
            args = options

        if args.debug:
            IS_DEBUG = True
        else:
            IS_DEBUG = False

        LOCAL_PORT = args.port
        LOCAL_IP = args.ip
