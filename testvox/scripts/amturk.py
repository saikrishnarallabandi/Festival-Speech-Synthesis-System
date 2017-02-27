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
##  Date  : August 2012                                                  ##
###########################################################################
"""Utility to upload and manage HITs on Mechanical Turk"""

from __future__ import print_function

from datetime import datetime, timedelta
import os
import pickle
import sys

boto_package_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                 'boto.zip')
sys.path.append(boto_package_file)
yaml_package_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                 '..', 'ext_tools', 'yaml.zip')
sys.path.append(yaml_package_file)
yaml_package_file2 = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                  '..', 'webserver', 'ext_tools', 'yaml.zip')
sys.path.append(yaml_package_file2)

import yaml


try:
    from boto.exception import NoAuthHandlerFound
    from boto.mturk.connection import MTurkConnection, MTurkRequestError
    from boto.mturk.price import Price
    from boto.mturk.question import ExternalQuestion
    from boto.mturk.qualification import Qualifications
    from boto.mturk.qualification import PercentAssignmentsApprovedRequirement
    from boto.mturk.qualification import LocaleRequirement
except ImportError:
    print("Python package boto not found.")
    print("Please run the download_boto.py script before running this script.")
    sys.exit(1)


def read_config_file(filename):
    """Reads the modifiable and binary sections of a given config file

    Arguments:
    - `filename`: Auto-generated YAML config file

    """
    config_readable = yaml.load(open(filename).read())
    config_binary = pickle.loads(config_readable['tv_experiment_details'])
    del config_readable['tv_experiment_details']
    return config_readable, config_binary


def write_config_file(filename, readable, binary):
    """Writes a config file with readable and binary sections that are
    each dicts.

    """
    with open(filename, "w+") as fout:
        fout.write(yaml.dump(readable, default_flow_style=False))
        fout.write('\n'.join(['', '# Do not modify below', '']))
        fout.write(yaml.dump({'tv_experiment_details':
                              pickle.dumps(binary,
                                           pickle.HIGHEST_PROTOCOL)},
                             default_flow_style=False))

# List of valid ISO-3166 country codes for Locale Requirements
valid_countries = ['AF', 'AX', 'AL', 'DZ', 'AS', 'AD', 'AO',
                   'AI', 'AQ', 'AG', 'AR', 'AM', 'AW', 'AU',
                   'AT', 'AZ', 'BS', 'BH', 'BD', 'BB', 'BY',
                   'BE', 'BZ', 'BJ', 'BM', 'BT', 'BO', 'BQ',
                   'BA', 'BW', 'BV', 'BR', 'IO', 'BN', 'BG',
                   'BF', 'BI', 'KH', 'CM', 'CA', 'CV', 'KY',
                   'CF', 'TD', 'CL', 'CN', 'CX', 'CC', 'CO',
                   'KM', 'CG', 'CD', 'CK', 'CR', 'CI', 'HR',
                   'CU', 'CW', 'CY', 'CZ', 'DK', 'DJ', 'DM',
                   'DO', 'EC', 'EG', 'SV', 'GQ', 'ER', 'EE',
                   'ET', 'FK', 'FO', 'FJ', 'FI', 'FR', 'GF',
                   'PF', 'TF', 'GA', 'GM', 'GE', 'DE', 'GH',
                   'GI', 'GR', 'GL', 'GD', 'GP', 'GU', 'GT',
                   'GG', 'GN', 'GW', 'GY', 'HT', 'HM', 'VA',
                   'HN', 'HK', 'HU', 'IS', 'IN', 'ID', 'IR',
                   'IQ', 'IE', 'IM', 'IL', 'IT', 'JM', 'JP',
                   'JE', 'JO', 'KZ', 'KE', 'KI', 'KP', 'KR',
                   'KW', 'KG', 'LA', 'LV', 'LB', 'LS', 'LR',
                   'LY', 'LI', 'LT', 'LU', 'MO', 'MK', 'MG',
                   'MW', 'MY', 'MV', 'ML', 'MT', 'MH', 'MQ',
                   'MR', 'MU', 'YT', 'MX', 'FM', 'MD', 'MC',
                   'MN', 'ME', 'MS', 'MA', 'MZ', 'MM', 'NA',
                   'NR', 'NP', 'NL', 'NC', 'NZ', 'NI', 'NE',
                   'NG', 'NU', 'NF', 'MP', 'NO', 'OM', 'PK',
                   'PW', 'PS', 'PA', 'PG', 'PY', 'PE', 'PH',
                   'PN', 'PL', 'PT', 'PR', 'QA', 'RE', 'RO',
                   'RU', 'RW', 'BL', 'SH', 'KN', 'LC', 'MF',
                   'PM', 'VC', 'WS', 'SM', 'ST', 'SA', 'SN',
                   'RS', 'SC', 'SL', 'SG', 'SX', 'SK', 'SI',
                   'SB', 'SO', 'ZA', 'GS', 'SS', 'ES', 'LK',
                   'SD', 'SR', 'SJ', 'SZ', 'SE', 'CH', 'SY',
                   'TW', 'TJ', 'TZ', 'TH', 'TL', 'TG', 'TK',
                   'TO', 'TT', 'TN', 'TR', 'TM', 'TC', 'TV',
                   'UG', 'UA', 'AE', 'GB', 'US', 'UM', 'UY',
                   'UZ', 'VU', 'VE', 'VN', 'VG', 'VI', 'WF',
                   'EH', 'YE', 'ZM', 'ZW']


class AMTurk:
    """Class that handles creating and managing HITs"""
    def __init__(self, live_turk=False):
        """Connect to MTurk. Sandbox is enabled by default"""
        if not live_turk:
            host = 'mechanicalturk.sandbox.amazonaws.com'
            print('\n'.join(["*" * 20,
                             'Using AMTurk Sandbox',
                             "*" * 20]))
        else:
            host = 'mechanicalturk.amazonaws.com'
            print('\n'.join(["*" * 20,
                             'Using AMTurk Live',
                             "*" * 20]))
        try:
            self.conn = MTurkConnection(host=host)
        except NoAuthHandlerFound:
            aws_key_url = ''.join(['https://aws-portal.amazon.com/',
                                   'gp/aws/developer/account/index.html',
                                   '?ie=UTF8&action=access-key'])

            print('\n'.join(["Authentication details missing.",
                             "Find your AWS keys at",
                             aws_key_url,
                             "Please create a file ~/.boto as follows:",
                             "",
                             "[Credentials]",
                             "aws_access_key_id = <your access key>",
                             "aws_secret_access_key = <your secret key>",
                             ""]))
            sys.exit(1)

    def _yesorexit(self):
        res = raw_input("Are you sure you want to continue? (yes or no) : ")
        if res.strip() == 'yes':
            return True
        else:
            print("Aborting...")
            sys.exit(1)

    def bal(self, args):
        print(self.conn.get_account_balance())

    def posttask(self, args):
        readable, binary = read_config_file(args.configfile)
        if 'hit_list' in binary:
            # Hits were already posted. Abandon
            print("This experiment has already been posted.")
            sys.exit(1)

        # Get the posting details
        exp_id = binary['exp_id']
        title = readable['hit_title']
        desc = readable['hit_description']
        keywords = readable['hit_keywords']
        base_url = readable['testvox_base_url']

        num_hits = binary['num_hits']
        price_per_assignment = args.price_per_assignment
        workers_per_hit = args.workers_per_hit

        # Country related restriction
        limit_to_country = args.limit_to_country
        if limit_to_country and limit_to_country not in valid_countries:
            print("Invalid Country code %s" % limit_to_country)
            sys.exit(1)

        # Get Confirmation
        print('\n'.join(['Posting %d hits' % num_hits,
                         '%d workers per hit' % workers_per_hit,
                         'Price %1.3f per assignment' % price_per_assignment]))
        worker_cost = num_hits * workers_per_hit * price_per_assignment
        if price_per_assignment > 0.05:
            commission = (worker_cost * 0.10)
        else:
            commission = 0.005 * num_hits * workers_per_hit
        total_cost = worker_cost + commission
        print('\n'.join(['Total cost Estimate: %1.2f' % total_cost,
                         'Account Bal: %s' % self.conn.get_account_balance()]))

        if limit_to_country:
            print('Hits Limited to: %s' % limit_to_country)
        else:
            print('Hits available in all countries')

        print("Posting task to AMTurk")
        self._yesorexit()

        # Set up Qualifications
        qualifications = Qualifications()
        qualifications.add(
            PercentAssignmentsApprovedRequirement('GreaterThan',
                                                  args.approval_percentage))

        if limit_to_country:
            qualifications.add(
                LocaleRequirement('EqualTo', limit_to_country))

        # Setup reward
        reward = Price(price_per_assignment, 'USD')

        # Setup HIT Type
        hit_type = self.conn.register_hit_type(
            title=title,
            description=desc,
            reward=reward,
            duration=60 * 20,  # duration in seconds
            keywords=', '.join(keywords),
            approval_delay=86400 * 7,
            qual_req=qualifications)

        hit_type = hit_type[0].HITTypeId

        print("Hit Type: %s" % hit_type)
        binary['hit_type'] = hit_type

        # Setup HITs
        hit_url_format = "%s/begin?exp_id=%s&amp;subtask_id=%d"

        hit_list = []
        for i in range(num_hits):
            url = hit_url_format % (base_url, exp_id, i)
            question = ExternalQuestion(url, 500)  # frame height
            hits = self.conn.create_hit(hit_type=hit_type,
                                        question=question,
                                        lifetime=timedelta(days=3),
                                        max_assignments=workers_per_hit)
            for hit in hits:
                print("Created HIT %s" % hit.HITId)
                hit_list.append(hit)
        binary['hit_list'] = hit_list

        write_config_file(args.configfile, readable, binary)

    def deletetask(self, args):
        """Auto-approve and delete all HITs for given task"""

        readable, binary = read_config_file(args.configfile)
        if 'hit_list' not in binary:
            print("This experiment has not been posted to AMTurk")
            sys.exit(1)

        print("Deleting HITs from AMTurk for experiment %s" % binary['exp_id'])
        print("This will approve all hits and delete them")

        self._yesorexit()

        for hit in binary['hit_list']:
            print("Disposing HIT %s\t" % hit.HITId, end='')
            try:
                self.conn.disable_hit(hit.HITId)
            except MTurkRequestError as err:
                if err.error_code == 'AWS.MechanicalTurk.InvalidHITState':
                    print("Already Deleted")
                else:
                    raise err
            else:
                print("Success")

        del binary['hit_list']
        write_config_file(args.configfile, readable, binary)

    def listassignments(self, args):
        """Get a list of completed assignments, with how long workers
        took do do it

        """
        readable, binary = read_config_file(args.configfile)
        if 'hit_list' not in binary:
            print("This experiment has not been posted to AMTurk")
            sys.exit(1)

        formatstr = "%30s %30s  %15s  %15s  %s"
        print(formatstr % ('hit_id',
                           'assignment_id',
                           'worker_id',
                           'status',
                           'seconds_spent'))

        for hit in binary['hit_list']:
            assignments = self.conn.get_assignments(hit_id=hit.HITId)
            if not assignments.NumResults:
                # Ignore this HIT
                continue
            hit_id = hit.HITId

            for ass in assignments:
                assignment_id = ass.AssignmentId
                worker_id = ass.WorkerId
                assignment_status = ass.AssignmentStatus

                starttime = datetime.strptime(ass.AcceptTime,
                                              '%Y-%m-%dT%H:%M:%SZ')
                endtime = datetime.strptime(ass.SubmitTime,
                                            '%Y-%m-%dT%H:%M:%SZ')
                assignment_time_spent = (endtime - starttime).total_seconds()

                print(formatstr % (hit_id,
                                   assignment_id,
                                   worker_id,
                                   assignment_status,
                                   assignment_time_spent))

    def approveall(self, args):
        """Approve all submissions on this task"""
        readable, binary = read_config_file(args.configfile)
        if 'hit_list' not in binary:
            print("This experiment has not been posted to AMTurk")
            sys.exit(1)

        approve_message = 'Thank you very much for your time!'

        print("Approve ALL submissions to experiment %s." % binary['exp_id'])
        print("You can NOT undo this.")

        self._yesorexit()

        for hit in binary['hit_list']:
            assignments = self.conn.get_assignments(hit_id=hit.HITId)
            if not assignments.NumResults:
                # Ignore this HIT
                continue
            for ass in assignments:
                print("%s \t" % ass.AssignmentId, end='')
                try:
                    self.conn.approve_assignment(
                        ass.AssignmentId, approve_message)
                except Exception as err:
                    state_error = "AWS.MechanicalTurk.InvalidAssignmentState"
                    if err.error_code == state_error:
                        print("Previously %s" % ass.AssignmentStatus)
                    else:
                        raise err
                else:
                    print("Approved")

    def reject(self, args):
        """Reject assignments if finished too quickly"""
        readable, binary = read_config_file(args.configfile)
        if 'hit_list' not in binary:
            print("This experiment has not been posted to AMTurk")
            sys.exit(1)

        reject_message = 'Sorry, we could not accept this submission'

        reject_candidates = []
        for hit in binary['hit_list']:
            assignments = self.conn.get_assignments(hit_id=hit.HITId)
            if not assignments.NumResults:
                # Ignore this HIT
                continue
            for ass in assignments:
                if ass.AssignmentStatus != 'Submitted':
                    # Can't review this
                    continue
                assignment_starttime = datetime.strptime(
                    ass.AcceptTime, "%Y-%m-%dT%H:%M:%SZ")
                assignment_endtime = datetime.strptime(
                    ass.SubmitTime, "%Y-%m-%dT%H:%M:%SZ")
                assignment_time_spent = (
                    assignment_endtime - assignment_starttime).total_seconds()

                if args.min_time > 0:
                    if assignment_time_spent < int(args.min_time):
                        # Reject this response
                        assignment_id = ass.AssignmentId
                        reject_candidates.append(assignment_id)
                        print(' '.join(["HIT:%30s" % hit.HITId,
                                        "Assignment:%30s" % assignment_id,
                                        "Worker:%20s" % ass.WorkerId,
                                        "Time:%d s" % assignment_time_spent]))

        if not reject_candidates:
            print("Nothing to reject")
            sys.exit(0)

        print("Rejecting %d assignments." % len(reject_candidates))
        self._yesorexit()
        print("You will disappoint these workers. Really.")
        self._yesorexit()

        for assignment_id in reject_candidates:
            print("%s \t" % assignment_id, end='')
            try:
                self.conn.reject_assignment(assignment_id, reject_message)
            except Exception as err:
                state_error = "AWS.MechanicalTurk.InvalidAssignmentState"
                if err.error_code == state_error:
                    print("Previously %s" % ass.AssignmentStatus)
                    pass
                else:
                    raise err
            else:
                print("Rejected")


if __name__ == '__main__':
    try:
        import argparse
    except ImportError:
        print("This script needs Python >= 2.7")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description='Create and manage HITs for experiments')
    parser.add_argument('-l', '--live-turk',
                        action='store_true',
                        default=False,
                        help='Run on live M-turk instead of the sandbox')
    subparsers = parser.add_subparsers(
        help='Different actions you could perform',
        dest='action')

    # Check Balance
    parser_bal = subparsers.add_parser('bal',
                                       help='Query available funds')

    # Post New Hits
    parser_post_hit = subparsers.add_parser('posttask',
                                            help='Post HITs')
    parser_post_hit.add_argument(
        '-w', '--workers-per-hit',
        type=int,
        help='Number of participants per HIT',
        default=10)
    parser_post_hit.add_argument(
        '-f', '--configfile', required=True,
        help='AMTurk config file generated by TestVox Admin')
    parser_post_hit.add_argument(
        '-a', '--approval-percentage',
        type=int,
        help='Worker qualification Approval percentage',
        default=80)
    parser_post_hit.add_argument(
        '-p', '--price-per-assignment',
        type=float,
        help='Price to pay participant per HIT',
        default=0.02)

    parser_post_hit.add_argument(
        '-c', '--limit-to-country',
        type=str,
        help='Restrict HIT to COUNTRY (Valid ISO-3166 Country Code) e.g. US',
        default='')

    # Delete posted HITs
    parser_delete_hit = subparsers.add_parser('deletetask',
                                              help='Delete HITs')
    parser_delete_hit.add_argument(
        '-f', '--configfile', required=True,
        help='AMTurk config file generated by TestVox')

    # Get list of assignments
    parser_list_assignments = subparsers.add_parser(
        'listassignments',
        help='List Assignments and Completion Time')

    parser_list_assignments.add_argument(
        '-f', '--configfile', required=True,
        help='AMTurk config file generated by TestVox')

    # Approve all assignments
    parser_approve_all = subparsers.add_parser('approveall',
                                               help='Approve all assignments')
    parser_approve_all.add_argument(
        '-f', '--configfile', required=True,
        help='AMTurk config file generated by TestVox')

    # Reject assignments
    parser_reject_assigns = subparsers.add_parser('reject',
                                                  help='Reject assignments')
    parser_reject_assigns.add_argument(
        '-t', '--min-time',
        help='Reject assignments finished in fewer than TIME seconds',
        metavar='TIME', required=True)
    parser_reject_assigns.add_argument(
        '-f', '--configfile', required=True,
        help='AMTurk config file generated by TestVox')

    # Now parse the arguments
    args = parser.parse_args()

    # Create turk object
    amturk = AMTurk(args.live_turk)

    # Run requested function
    func = getattr(amturk, args.action)
    func(args)
