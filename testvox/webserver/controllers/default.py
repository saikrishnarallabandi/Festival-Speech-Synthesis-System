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
"""Handler for default (non-json) urls for TestVox"""

import cherrypy
import csv
import datetime
import logging
import os
import pickle
import yaml
import StringIO
import sys

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader(
    os.path.join(os.path.abspath(os.path.dirname(__file__)),
                 '..', 'views', 'templates')))

from models import experiments
from models.db import db

try:
    from controllers import gen_auth
except ImportError:
    print("Please run scripts/change_admin_password.py before starting server")
    sys.exit(1)

logger = logging.getLogger(__name__)


class TestVoxRoot:
    @cherrypy.expose
    @cherrypy.tools.expires(secs=3600 * 24 * 365)
    def index(self):
        """Requests to / lead to a default landing page"""

        template = env.get_template('index.html')
        return template.render()

    def error(self, code=404):
        """ Inform user of an error in processing their request"""
        if code == 404:
            raise cherrypy.HTTPError(code, "Page not Found")
        else:
            raise cherrypy.HTTPError(code, "Unknown Error")

    @cherrypy.expose
    def begin(self, *args, **kwargs):
        """This function begins a new experiment. It obtains relevant
        variables from the request (such as, identity of participant,
        experiment details, etc.) and stores these values in the
        session. It then simply redirects the user to the
        testvox_client, which will use JSON RPC to retrieve the saved
        experiment data to run the evaluation.

        """
        try:
            exp_id = kwargs['exp_id']
        except KeyError:
            # Experiment ID MUST be set.
            self.error(400)

        username = ''

        # Set up for handling AMTurk requests
        amturk_mode = None  # 'local', 'preview' or 'accepted', or 'test'
        amturk_hit_id = None
        amturk_assignment_id = None
        amturk_worker_id = None
        amturk_submit_url = None

        try:
            # Figure out if we are in AMTurk mode.

            # hitID and assignmentID are the variables that AMTurk
            # sets for us to use. In AMTurk preview mode, the
            # assignmentID is set to ASSIGNMENT_ID_NOT_AVAILABLE.
            amturk_hit_id = kwargs['hitId']
            amturk_assignment_id = kwargs['assignmentId']
        except KeyError:
            amturk_mode = 'local'

        if amturk_assignment_id == 'ASSIGNMENT_ID_NOT_AVAILABLE':
            amturk_mode = 'preview'
        elif amturk_assignment_id is not None:
            # Since we are not in preview, workerId and
            # turkSubmitTo URL must be set!
            try:
                amturk_worker_id = kwargs['workerId']
                amturk_submit_url = kwargs['turkSubmitTo']

                # Set the username variable to be workerID
                username = 'amturk_%s' % amturk_worker_id
            except KeyError:
                # This is an error.
                self.error(400)

        if amturk_mode == 'local':
            # Get the username from the request
            try:
                username = kwargs['username']
            except KeyError:
                # We don't want anonymous users.
                # Redirect them to a page that asks them for their name

                raise cherrypy.HTTPRedirect(
                    '/begin_with_name?exp_id=%s' % exp_id)

            # Test user
            if username == 'testvox_test':
                amturk_mode = 'test'

            # For local testing, we can get the username from the
            # request. If this is not set, we ask the participant to
            # enter their name on a form. This only applies to local
            # testing. AMTurk workers have their ID set in the
            # requests.

            # Local usernames must be converted to UID. This is done
            # by saving the IP and TIME as part of the username
            user_ip = cherrypy.request.remote.ip
            current_time = datetime.datetime.now()
            username = '%s_%s_%s' % (username,
                                     user_ip,
                                     current_time)

        try:
            subtask_id = int(kwargs['subtask_id'])
        except KeyError:
            subtask_id = None

        # Now store session variables
        cherrypy.session['exp_id'] = exp_id
        cherrypy.session['subtask_id'] = subtask_id
        cherrypy.session['exp_progress'] = 0
        cherrypy.session['username'] = username
        cherrypy.session['amturk_mode'] = amturk_mode
        cherrypy.session['amturk_hit_id'] = amturk_hit_id
        cherrypy.session['amturk_assignment_id'] = amturk_assignment_id
        cherrypy.session['amturk_worker_id'] = amturk_worker_id
        cherrypy.session['amturk_submit_url'] = amturk_submit_url

        if amturk_mode == 'preview' or amturk_mode == 'test':
            cherrypy.session['is_preview'] = True
        else:
            cherrypy.session['is_preview'] = False

        # Now send user to the web client
        raise cherrypy.HTTPRedirect(
            '/static/testvox_client/testvox_client.html')

    @cherrypy.expose
    def begin_with_name(self, exp_id):
        """This function begins a new experiment. It obtains relevant
        variables from the request (such as, identity of participant,
        experiment details, etc.) and stores these values in the
        session. It then simply redirects the user to the
        testvox_client, which will use JSON RPC to retrieve the saved
        experiment data to run the evaluation.

        """
        template = env.get_template('query_participant_name.html')
        return template.render(exp_id=exp_id)

    @cherrypy.expose
    def media(self, exp_id, *args, **kwargs):
        """Serves audio requests. exp_id is used for cache-busting on
        browser side

        """
        # filename is actually in args
        filename = '/'.join(args)

        exp_id = cherrypy.session['exp_id']
        experiment = experiments.Experiment(exp_id)

        mime_map = {
            'mp3': 'audio/mpeg3'
        }

        try:
            content_type = mime_map[filename.split('.')[-1]]
        except KeyError:
            content_type = 'application/unknown'

        cherrypy.response.headers['Content-Type'] = content_type
        return experiment.get_mediafile(filename)

    @cherrypy.expose
    def admin(self, *args, **kwargs):
        try:
            page = kwargs['page']
        except KeyError:
            page = 'home'

        if page == 'home':
            exp_list = experiments.get_experiments()
            template = env.get_template('admin_home.html')
            return template.render(exp_list=exp_list)

        if page == 'upload_experiment':
            exp_file = None
            try:
                exp_file = kwargs['exp_file']
            except:
                error = 'No file submitted'

            try:
                description = kwargs['description']
            except:
                description = 'No description'

            if exp_file:
                error = experiments.add_experiment(description, exp_file.file)
            exp_list = experiments.get_experiments()
            template = env.get_template('admin_home.html')
            return template.render(exp_list=exp_list, error=error)

        if page == 'download_amturk_config':
            error = ''
            try:
                exp_id = kwargs['exp_id']
            except KeyError:
                error = "Experiment not specified"
            else:
                experiment = experiments.Experiment(exp_id)
                if not experiment:
                    error = "Could not retrieve experiment %s" % exp_id
                config = experiment.get_config()
                if not config:
                    error = "Invalid configuration in experiment %s" % exp_id
                else:
                    try:
                        config['testvox_amturk_config']
                    except KeyError:
                        error = ' '.join(['Experiment %s' % exp_id,
                                          'is not configured'
                                          'for AMTurk'])
            if error:
                exp_list = experiments.get_experiments()
                template = env.get_template('admin_home.html')
                return template.render(exp_list=exp_list, error=error)

            amturk_conf_immutable = {
                'exp_id': exp_id,
                'num_hits': config['testvox_amturk_config']['num_hits']
            }

            config = {
                'hit_title': 'Type a 5--6 word task description',
                'hit_description': 'Type a short task description',
                'hit_keywords': ['audio', 'speech', 'keyword3'],
                'testvox_base_url': cherrypy.request.base,
            }

            output = yaml.dump(config, default_flow_style=False)
            output = output + '\n' + '# Do not Edit Below\n'
            output = output + yaml.dump({
                'tv_experiment_details': pickle.dumps(amturk_conf_immutable,
                                                      pickle.HIGHEST_PROTOCOL)
            }, default_flow_style=False)

            cherrypy.response.headers['Content-Type'] = 'text/x-yaml'
            cdisp = 'attachment; filename=amturk_config_%s.yaml' % exp_id
            cherrypy.response.headers['Content-Disposition'] = cdisp
            return output

        if page == 'download_results':
            error = ''
            try:
                exp_id = kwargs['exp_id']
            except KeyError:
                error = "Experiment not specified"
            else:
                experiment = experiments.Experiment(exp_id)
                if not experiment:
                    error = "Could not retrieve experiment %s" % exp_id
            if error:
                exp_list = experiments.get_experiments()
                template = env.get_template('admin_home.html')
                return template.render(exp_list=exp_list, error=error)

            config = experiment.get_config()
            # Determine the fields in results
            # one field per question in survey
            # and one field per data item in listening task
            fields = []
            for step in config['testvox_steps']:
                if step['task_type'] == 'surveyform':
                    fields.extend(
                        [str(x['name']) for x in step['questions']])
                else:
                    try:
                        fields.extend(
                            [str(x['name']) for x in step['data']])
                    except KeyError:
                        # Use 'filename' if 'name' is not defined
                        fields.extend(
                            [str(x['filename']) for x in step['data']])

            # Now read the surveys for this experiment and build a dict
            surveys = db(
                db.participant_surveys.survey_scope == exp_id).select()
            participant_submission = {}
            for survey in surveys:
                participant_uid = survey.participant_uid
                info = {}
                survey_data = pickle.loads(survey.survey_data)
                for item in survey_data:
                    name = item['name']
                    response = item['response']
                    if name not in fields:
                        continue
                    info[name] = response
                try:
                    participant_submission[participant_uid].update(
                        info)
                except KeyError:
                    participant_submission[participant_uid] = info

            # Now read the listening tests, and update rows as we go.
            # This assumes one person only takes the test once.
            listening_results = db(
                db.listening_tasks.experiment_uid == exp_id).select()
            for res in listening_results:
                participant_uid = res.participant_uid
                rowitem = {res.task_data_name: pickle.loads(
                    res.task_data_response)}
                try:
                    participant_submission[participant_uid].update(rowitem)
                except:
                    participant_submission[participant_uid] = rowitem

            # Now create a CSV file
            csvio = StringIO.StringIO()
            fieldnames = ['participant_uid']
            fieldnames.extend(fields)
            out = csv.DictWriter(csvio, fieldnames)
            try:
                out.writeheader()
            except AttributeError:
                # writeheader only introduced in Python 2.7
                row = {}
                for x in fieldnames:
                    row[x] = x
                out.writerow(row)
            for participant_uid in participant_submission:
                row = {'participant_uid': participant_uid}
                row.update(participant_submission[participant_uid])
                out.writerow(row)
            cherrypy.response.headers['Content-Type'] = 'text/csv'
            cdisp = 'attachment; filename=testvox_results_%s.csv' % exp_id
            cherrypy.response.headers['Content-Disposition'] = cdisp
            return csvio.getvalue()

        if page == 'download':
            error = ''
            try:
                exp_id = kwargs['exp_id']
            except KeyError:
                error = "Experiment not specified"
            else:
                zip = experiments.get_experiment_raw_zipfile(exp_id)
                if not zip:
                    error = "Could not retrieve experiment %s" % exp_id
            if error:
                exp_list = experiments.get_experiments()
                template = env.get_template('admin_home.html')
                return template.render(exp_list=exp_list, error=error)
            else:
                cherrypy.response.headers['Content-Type'] = 'application/zip'
                cdisp = 'attachment; filename=testvox_%s.zip' % exp_id
                cherrypy.response.headers['Content-Disposition'] = cdisp
                return zip

        if page == 'delete':
            error = ''
            try:
                exp_id = kwargs['exp_id']
            except KeyError:
                error = "Experiment not specified"
            else:
                success = experiments.delete_experiment(exp_id)
                if success:
                    raise cherrypy.HTTPRedirect('/admin')

                if not success:
                    error = "Could not delete experiment %s" % exp_id
            exp_list = experiments.get_experiments()
            template = env.get_template('admin_home.html')
            return template.render(exp_list=exp_list, error=error)

    admin._cp_config = {
        'tools.auth_digest.on': True,
        'tools.auth_digest.realm': gen_auth.realm,
        'tools.auth_digest.get_ha1': gen_auth.get_ha1,
        'tools.auth_digest.key': gen_auth.digest_key}
