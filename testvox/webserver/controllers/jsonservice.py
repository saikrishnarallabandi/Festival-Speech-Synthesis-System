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
"""JSON RPC service to handle TestVox client (PYJS)"""

import cherrypy
import datetime
import hashlib
import itertools
import logging
import pickle
import sys
import traceback
from urllib import urlencode

if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json

from models import experiments
from models.db import db

logger = logging.getLogger(__name__)


class JSONRPCServiceBase:
    def response(self, message_id, result):
        """Return a response for given method"""
        return json.dumps({'jsonrpc': '2.0', 'id': message_id,
                'result': result, 'error': None})

    def error(self, message_id, code, message):
        return json.dumps({'id': message_id,
                           'jsonrpc': '2.0',
                           'error': {'name': 'JSONRPCError',
                                     'code': code,
                                     'message': message
                                 }})

    @cherrypy.expose
    def default(self, *args):
        try:
            request = json.loads(cherrypy.request.body.read())
        except TypeError:
            return self.error(0, -32700,
                              'Invalid Request')

        message_id = request['id']
        method = request['method']
        params = request['params']

        try:
            func = getattr(self, method)
            return self.response(message_id,
                                 func(*params))
        except AttributeError:
            return self.error(message_id, -32601,
                              'method "%s" does not exist' % method)
        except:
            etype, eval, etb = sys.exc_info()
            tb = traceback.format_tb(etb)
            return self.error(message_id,
                              -32602,
                              '%s: %s\n%s' % \
                              (etype.__name__, eval, '\n'.join(tb)))


class TestVoxService(JSONRPCServiceBase):
    def get_next_task(self, params):
        """
        Send information about the next available task.

        params: data submitted from the previous task (if any)
        """
        exp_id = cherrypy.session.get('exp_id')
        subtask_id = cherrypy.session.get('subtask_id')
        experiment = experiments.Experiment(exp_id)
        config = experiment.get_config()
        cherrypy.session['exp_config'] = config

        cur_progress = cherrypy.session.get('exp_progress')

        try:
            task_to_show = config['testvox_steps'][cur_progress]
        except IndexError:
            # Refresh on finish page can cause this
            task_to_show = {'name': 'finished',
                            'task_type': 'finished',
                            'submit_url': None}

            task_to_show['is_preview'] = cherrypy.session.get('is_preview')
            task_to_show['exp_id'] = cherrypy.session.get('exp_id')
            return task_to_show

        try:
            # Detect if current task is being submitted
            cur_task_name = task_to_show['name']
            task_submission = params[cur_task_name]
        except KeyError:
            # No valid submission made. Show the current task.
            pass
        else:
            # Submission was valid.
            # Save it to a database if not in preview mode
            if not cherrypy.session.get('is_preview'):
                if task_to_show['task_type'] == 'surveyform':
                    # A survey result was submitted
                    participant_uid = cherrypy.session.get('username')

                    survey_uid = hashlib.md5(str(task_to_show)).hexdigest()

                    try:
                        survey_scope = task_to_show['survey_scope']
                    except KeyError:
                        survey_scope = 'experiment'

                    if survey_scope == 'experiment':
                        survey_scope = exp_id

                    survey_data = pickle.dumps(task_submission)

                    submission_time = datetime.datetime.now()

                    db.participant_surveys.insert(
                        participant_uid=participant_uid,
                        survey_uid=survey_uid,
                        survey_scope=survey_scope,
                        survey_data=survey_data,
                        submission_time=submission_time)
                    db.commit()
                else:
                    # A listening task was submitted
                    participant_uid = cherrypy.session.get('username')
                    submission_time = datetime.datetime.now()
                    # task_submission is a list of dicts:
                    # { 'name': name,
                    #   'response': response,
                    #   'extra_info': extra_info}

                    for item in task_submission:
                        name = item['data_name']
                        response = pickle.dumps(item['data_response'])
                        extra_info = pickle.dumps(item['data_extra_info'])
                        db.listening_tasks.insert(
                            participant_uid=participant_uid,
                            experiment_uid=exp_id,
                            task_data_name=name,
                            task_data_response=response,
                            task_data_extra_info=extra_info,
                            submission_time=submission_time)
                    db.commit()
                    pass

            cur_progress += 1
            cherrypy.session['exp_progress'] = cur_progress

        try:
            while True:
                task_to_show = config['testvox_steps'][cur_progress]
                if task_to_show['task_type'] == 'surveyform':
                    if cherrypy.session.get('amturk_mode') == 'preview':
                        cur_progress += 1
                        cherrypy.session['exp_progress'] = cur_progress
                        continue
                    else:
                        # see if this participant has already taken the survey
                        user = cherrypy.session.get('username')
                        survey_uid = hashlib.md5(str(task_to_show)).hexdigest()
                        try:
                            scope = task_to_show['survey_scope']
                        except KeyError:
                            scope = 'experiment'

                        if scope == 'experiment':
                            scope = exp_id

                        row = db(
                            (db.participant_surveys.participant_uid == user) &
                            (db.participant_surveys.survey_uid == survey_uid) &
                            (db.participant_surveys.survey_scope == scope)
                        ).select().first()

                        if row is None:
                            # user has not taken this survey
                            break
                        else:
                            cur_progress += 1
                            cherrypy.session['exp_progress'] = cur_progress
                            continue
                else:
                    break

        except IndexError:
            # Done with everything
            # Post just a simple flag to m-turk.
            query_params = {
                'assignmentId': cherrypy.session.get('amturk_assignment_id'),
                'workerId': cherrypy.session.get('amturk_worker_id'),
                'value': 1,
                'exp_id': exp_id}

            if cherrypy.session.get('amturk_submit_url') is not None:
                submit_url = "%s/mturk/externalSubmit?%s" % (
                    cherrypy.session.get('amturk_submit_url'),
                    urlencode(query_params))
            else:
                submit_url = None

            task_to_show = {'name': 'finished',
                            'task_type': 'finished',
                            'submit_url': submit_url}

        task_to_show['is_preview'] = cherrypy.session.get('is_preview')
        task_to_show['exp_id'] = cherrypy.session.get('exp_id')
        task_to_show['testvox_config'] = config['testvox_config']

        # See if a specific partition of the task was requested
        try:
            amturk_config = config['testvox_amturk_config']
        except KeyError:
            # No need to partition
            return task_to_show

        # Tasks without 'data' section are not partitioned
        if 'data' not in task_to_show:
            return task_to_show

        # If partition is not requested, return everything
        if subtask_id is None:
            return task_to_show

        num_hits = amturk_config['num_hits']
        clips_per_hit = amturk_config['num_clips_per_hit']

        # Out of task_to_show['data'], we want partition number
        # subtask_id of num_hits. We can do that by using
        # itertools
        data_cycle = itertools.cycle(task_to_show['data'])

        # if exp_hit_partition is 0, we ignore first 0
        # items. Otherwise we ignore first exp_hit_partition items
        for i in range(subtask_id):
            data_cycle.next()

        # Now take every item at position num_hits
        new_data = []
        for idx, data_item in enumerate(data_cycle):
            if idx % num_hits == 0:
                new_data.append(data_item)
                if len(new_data) == clips_per_hit:
                    break

        task_to_show['data'] = new_data

        return task_to_show
