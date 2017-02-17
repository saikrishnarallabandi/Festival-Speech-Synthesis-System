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
"""TestVox web based service: The serverside component"""

import sys
import os

# Import cherrypy from zipfile
top_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(top_directory,
                                'ext_tools', 'cherrypy.zip'))
import cherrypy

# Add YAML to import path
sys.path.insert(0, os.path.join(top_directory,
                                'ext_tools', 'yaml.zip'))

# Add Jinja2 to import path
sys.path.insert(0, os.path.join(top_directory,
                                'ext_tools', 'jinja2.zip'))

# Detect Environment (Debug/GAE,etc)
import environ

from controllers.jsonservice import TestVoxService
from controllers.default import TestVoxRoot


app_conf = {
    '/favicon.ico': {
        'tools.staticfile.on': True,
        'tools.staticfile.filename': os.path.join(top_directory,
                                                  'views', 'static',
                                                  'images',
                                                  'favicon.ico'),
        'tools.expires.on': True,
        'tools.expires.secs': 3600 * 24 * 365,
        'tools.gzip.on': True,
        'tools.gzip.mime_types': ['image/*'],
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.root': top_directory,
        'tools.staticdir.dir': 'views/static',
        'tools.staticdir.content_types': {
            'html': 'text/html; charset=utf-8'},
        'tools.expires.on': True,
        'tools.expires.secs': 3600 * 24 * 365,
        'tools.sessions.on': False,
        'tools.gzip.on': True,
        'tools.gzip.mime_types': ['text/*',
                                  'image/*',
                                  'application/*'],
    }
}

server_conf = {
    'global': {}
}

if not environ.IS_DEBUG:
    server_conf['global']['environment'] = 'production'

if environ.IS_GAE:
    # App-Engine Specific Configuration

    # Stop having cherrypy log same stuff as gae
    cherrypy.log.access_log.propagate = False

    # Use data-store for sessions backend
    from models.sessions import GaeSession
    cherrypy.lib.sessions.GaeSession = GaeSession

    server_conf['global'].update({
        'tools.sessions.on': True,
        'tools.sessions.storage_type': 'gae',
        'tools.sessions.clean_freq': None,
        })
else:
    # Configure a locally running Cherrypy Server

    data_dir = environ.DATA_DIR
    log_dir = environ.LOG_DIR
    sessions_dir = environ.SESSIONS_DIR

    server_conf['global'].update({
        'log.access_file': os.path.join(log_dir, 'access.log'),
        'log.error_file': os.path.join(log_dir, 'error_log'),
        'server.socket_port': environ.LOCAL_PORT,
        'server.socket_host': environ.LOCAL_IP,
        'server.reverse_dns': False,
        'tools.sessions.on': True,
        'tools.sessions.storage_type': 'file',
        'tools.sessions.storage_path': environ.SESSIONS_DIR,
        'tools.sessions.timeout': 60,
    })

root = TestVoxRoot()
root.services = TestVoxService()

app = cherrypy.tree.mount(root, '/', app_conf)
cherrypy.config.update(server_conf)

if __name__ == '__main__':
    cherrypy.engine.start()
    cherrypy.engine.block()
