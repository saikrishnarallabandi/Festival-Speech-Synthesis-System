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
Sets up appropriate backends to use based on current runtime environment

"""


import environ
from ext_tools.dal import DAL, Field

db = None

if environ.IS_GAE:
    # We must use the google data store
    db = DAL('google:datastore')
else:
    _data_path = environ.DATA_DIR
    db = DAL('sqlite://data.db', folder=_data_path)


db.define_table('participant_surveys',
                Field('participant_uid', required=True,
                      comment='Unique ID of the participant'),
                Field('survey_uid', required=True,
                      comment='Unique ID of the survey form'),
                Field('survey_scope', required=True,
                      comment='global, or unique ID of experiment'),
                Field('survey_data', 'blob', required=True,
                      comment='actual survey data (a python dict)'),
                Field('submission_time', 'datetime', required=True,
                      comment='When the survey was submitted'))

db.define_table('experiments',
                Field('experiment_uid', unique=True),
                Field('description'),
                Field('zipfile', 'blob'),
                Field('upload_time', 'datetime'))

db.define_table('listening_tasks',
                Field('participant_uid', required=True,
                      comment='Unique ID of the participant'),
                Field('experiment_uid', required=True,
                      comment='Unique ID of the experiment'),
                Field('task_data_name', required=True,
                      comment='The unique ID of the task data item'),
                Field('task_data_response', 'blob', required=True,
                      comment='The response to that task data item'),
                Field('task_data_extra_info', 'blob',
                      comment='Extra task info, (a python dict)'),
                Field('submission_time', 'datetime', required=True,
                      comment='When the data item was submitted'))
