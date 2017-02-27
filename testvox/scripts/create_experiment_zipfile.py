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
"""Takes a TestVox Experiment Directory, verifies configuration and
builds a Zip file for upload to server

"""
from __future__ import print_function

import os
import sys

current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(current_dir, '..',
                             'ext_tools', 'yaml.zip'))  # prebuilt
sys.path.append(os.path.join(current_dir, '..', 'webserver',
                             'ext_tools', 'yaml.zip'))  # sources

import yaml
import zipfile


def die(message):
    print(message)
    sys.exit(1)


def verify_config(exp_dir):
    """
    Run a sanity check on the config file of the experiment
    Arguments:
    - `exp_dir`: Experiment Directory
    """
    configfile = os.path.join(exp_dir, 'config.yaml')
    try:
        config = yaml.load(open(configfile).read())
    except IOError:
        print("Config file not readable")
        return False
    except yaml.scanner.ScannerError:
        print("Config file is not a valid YAML file")
        print("Make sure indentation is correct")
        print("Make sure file has no tab character in it")
        return False

    def error(message):
        print(message)

    # Sanity Checks

    # 1. main sections of the file are present
    if not 'testvox_config' in config:
        error("Configuration is missing testvox_config section")
        return False
    if not 'testvox_steps' in config:
        error("Configuration is missing testvox_steps section")
        return False
    try:
        check = config['testvox_amturk_config']
    except KeyError:
        # optional section
        pass
    else:
        # But if it exists, it should contain num_hits and num_clips_per_hit
        if not 'num_hits' in check:
            error("num_hits must be specified under testvox_amturk_config")
            return False
        if not 'num_clips_per_hit' in check:
            error("num_clips_per_hit required under testvox_amturk_config")
            return False

    # 2. base_media_directory must be specified
    try:
        base_media_dir = config['testvox_config']['base_media_directory']
    except KeyError:
        error("You must specify base_media_directory in the configuration")
        return False

    if not os.path.exists(os.path.join(exp_dir,
                                       base_media_dir)):
        error("%s is not a valid relative path in  directory" % base_media_dir)
        return False
    # 3. testvox_steps should be nonempty
    if not config['testvox_steps']:
        error("You did not specify any testvox_steps")
        return False

    # 4. Check each testvox_step
    for step in config['testvox_steps']:
        try:
            check = step['name']
            task_type = step['task_type']
            check = step['instruction']
        except KeyError:
            error('\n'.join(["all testvox_steps items must have these keys:",
                             "name, task_type, instruction"]))
            return False
        if task_type == 'surveyform':
            try:
                questions = step['questions']
            except KeyError:
                error("Survey tasks must all have a questions section")
                return False
            for q in questions:
                try:
                    check = q['name']
                    t = q['type']
                    check = q['text']
                except KeyError:
                    error("Survey questions must have name, type and text")
                    return False
                if t in ['select', 'radio', 'check']:
                    try:
                        check = q['options']
                    except:
                        error(' '.join(["Select/Radio/Check questions",
                                        "must have options specified"]))
                        return False
        else:
            try:
                data = step['data']
                check = step['data_randomize']
            except KeyError:
                error(' '.join(["Listening tasks must all have",
                                "a data section",
                                "and a data_randomize entry"]))
                return False
            for item in data:
                try:
                    check = item['name']
                except KeyError:
                    try:
                        check = item['filename']
                    except KeyError:
                        error(' '.join(["Listening task data items",
                                        "must each have either a name",
                                        "or a filename key"]))
                        return False
            # sanitize A/B test
            if task_type == 'abtest':
                try:
                    check = step['directory_a']
                    check = step['directory_b']
                    check = step['ab_randomize']
                except KeyError:
                    error(' '.join(["A/B test needs these keys: ",
                                    "directory_a",
                                    "directory_b",
                                    "ab_randomize"]))
                    return False
            elif task_type == 'radiotask' or task_type == 'checktask':
                # sanitize radiotask
                try:
                    check = step['task_options']
                except KeyError:
                    error("Radio/Check tasks must have task_options specified")
                    return False
            elif task_type == 'wordchoicetask':
                # Sanitize wordchoicetask
                try:
                    check = step['select_type']
                except KeyError:
                    error('wordchoicetask steps must have a select_type')
                    return False
                for item in step['data']:
                    try:
                        check = item['filename']
                        text = item['text']
                        flags = item['enabled_flags']
                    except KeyError:
                        error(' '.join(["wordchoicetask data must have",
                                        "these keys:",
                                        "filename, text, enabled_flags"]))
                        return False
                    if not isinstance(flags, str):
                        error('enabled_flags must be enclosed in quotes')
                        return False
                    tokens = text.split()
                    if len(tokens) != len(flags):
                        error('\n'.join(["text: %s" % text,
                                        "flags: %s" % flags,
                                        "mismatch in length"]))
                        return False

        if check:  # Added to surpress lint errors
            check == ""

    # Sane config file
    print("Configuration File Verified")
    return True


def create_zip(exp_dir, outfile):
    """Create a zipfile for the experiment directory

    Arguments:
    - `exp_dir`: directory to zip
    - `outfile`: file to write
    """
    if os.path.exists(outfile):
        die("%s already exists. Not overwriting" % outfile)

    zf = zipfile.ZipFile(outfile, 'w', zipfile.ZIP_DEFLATED)

    exp_path = exp_dir[:-(len(os.path.basename(exp_dir)))]

    for dirpath, dirnames, filenames in os.walk(exp_dir,
                                                followlinks=True):
        arc_dirpath = dirpath[len(exp_path):]
        zf.write(dirpath, arc_dirpath)
        print("Adding %s" % dirpath)
        for f in filenames:
            print("Adding %s" % os.path.join(dirpath, f))
            zf.write(os.path.join(dirpath, f),
                     os.path.join(arc_dirpath, f))
    zf.close()
    print("%s written and ready for upload." % outfile)
    print("Good luck with your experiment!")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        die("Usage: %s experiment-directory output.zip")

    exp_dir = sys.argv[1]
    outfile = sys.argv[2]
    if verify_config(exp_dir):
        create_zip(exp_dir, outfile)
    else:
        die("Please fix configuration errors")
