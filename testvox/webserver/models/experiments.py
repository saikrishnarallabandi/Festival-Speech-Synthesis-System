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
"""Handling storage for experiments

Experiments are stored as zip files, either in file system (locally)
or in BlobStore (GAE) and the zipfile can be retrieved using the name
of the zipfile as the key

"""

import datetime
import hashlib
import os
import zipfile
import yaml

from StringIO import StringIO

from models.db import db

import environ

if environ.IS_GAE:
    from google.appengine.api import files
    from google.appengine.ext import blobstore


def get_experiments():
    """Queries the database for list of experiments Returns the id,
    name and description

    """

    rows = db().select(db.experiments.id,
                       db.experiments.experiment_uid,
                       db.experiments.description,
                       db.experiments.upload_time)

    for r in rows:
        config = Experiment(r.experiment_uid).get_config()
        r.error_corrupt_file = False if config else True

        try:
            num_hits = config['testvox_amturk_config']['num_hits']
        except KeyError:
            num_hits = 0
        r.num_hits = num_hits
    return rows


def add_experiment(description, fileobject):
    """fileobject is an uploaded zipfile, opened by cherrypy"""
    zf = None
    try:
        zf = zipfile.ZipFile(fileobject)
        zf.testzip()
    except:
        return "Could not read zip file"

    # Test that zf has a valid config
    exp = Experiment.create_from_zipfile(zf)
    config = exp.get_config()
    if not config:
        return "Uploaded file has invalid configuration. " \
            "Please use scripts/create_experiment_zipfile.py " \
            "to create files."

    # Get experiment ID based on contents
    exp_id = generate_experiment_uid(fileobject)
    fileobject.seek(0)
    data = fileobject.read()
    now = datetime.datetime.now()

    # If on GAE, we need to store file in blobstore, and store the key
    # in our database
    if environ.IS_GAE:
        fblobname = files.blobstore.create(
            mime_type='application/octet-stream')
        fblob = files.open(fblobname, 'a')
        fblob.write(data)
        fblob.close()
        files.finalize(fblobname)
        blob_key = files.blobstore.get_blob_key(fblobname)
        data = str(blob_key)

    try:
        db.experiments.insert(experiment_uid=exp_id,
                              description=description,
                              zipfile=data,
                              upload_time=now)
        db.commit()
    except Exception:
        return ' '.join(["Your experiment could not be saved to the database.",
                        "Possible Duplicate?"])


def generate_experiment_uid(fileobject):
    fileobject.seek(0)
    md5 = hashlib.md5()
    for chunk in iter(lambda: fileobject.read(8192), ''):
        md5.update(chunk)
    return md5.hexdigest()


def get_experiment_raw_zipfile(exp_id):
    """Returns raw zip data for given exp_id"""

    row = db(db.experiments.experiment_uid == exp_id).select().first()
    if row is None:
        return None

    if environ.IS_GAE:
        # Get key from database and file from blob
        blob_key = row.zipfile
        file_data = blobstore.BlobInfo.get(blob_key).open().read()
        return file_data
    else:
        return row.zipfile


def get_experiment_zipfile(exp_id):
    """Retrieve and return a zipfile.ZipFile for experiment. Returns
    None if experiment was not found

    Arguments:
    - `exp_id`: Unique ID for the experiment

    """
    zipdata = get_experiment_raw_zipfile(exp_id)
    if not zipfile:
        return None
    else:
        return zipfile.ZipFile(StringIO(zipdata))


def delete_experiment(exp_id):
    """Deletes experiment from database Also deletes all associated
    results.
    """
    success = db(db.experiments.experiment_uid == exp_id).delete()
    # Delete experiment results. There may not be any.
    db(
        db.participant_surveys.survey_scope == exp_id).delete()
    db(
        db.listening_tasks.experiment_uid == exp_id).delete()

    if success:
        db.commit()
        return True
    else:
        db.rollback()
        return False


class Experiment:

    """Load an experiment as a zipfile, and provide functionality to
    access entitities within the zipfile

    """

    def __init__(self, exp_id):
        self.exp_id = exp_id
        if exp_id is not None:
            self.zipfile = get_experiment_zipfile(exp_id)
        self.base_path = ''
        self.config = None

    @classmethod
    def create_from_zipfile(cls, zipfile):
        """Allows creating an experiment object from a zipfile
        directly, rather than via db lookup of an exp_id

        """
        exp = cls(None)
        exp.zipfile = zipfile
        return exp

    def _readfile(self, filename):
        """Read filename from the zip archive"""
        if self.zipfile is not None:
            if not self.base_path:
                for fname in self.zipfile.namelist():
                    if fname.endswith('config.yaml'):
                        self.base_path = os.path.dirname(fname)
                        break
            arcname = os.path.join(self.base_path, filename)
            try:
                return self.zipfile.read(arcname)
            except KeyError:
                return ""
        else:
            return ""

    def get_config(self):
        """Return the configuration of the current experiment.  Cache
        the configuration in this object. Retrieve from zip if not
        available

        """

        if self.config is None:
            try:
                self.config = yaml.load(self._readfile('config.yaml'))
            except yaml.YAMLError:
                self.config = {}
        if self.config is None:
            self.config = {}
        return self.config

    def get_mediafile(self, filename):
        """Return content of given file"""
        config = self.get_config()
        base_path = config['testvox_config']['base_media_directory']
        path = os.path.join(base_path, filename)
        return self._readfile(path)
