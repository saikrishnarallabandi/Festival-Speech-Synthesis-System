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
"""Session Storage models for Cherrypy (such as, using database)"""

import pickle
import time

import environ

from models.db import db, Field
from cherrypy.lib.sessions import Session

if environ.IS_GAE:
    from google.appengine.api import memcache

    class GaeSession(Session):
        """Implementation of the Google App Engine Datastore/Memcache
        Backend for sessions.

        """

        pickle_protocol = pickle.HIGHEST_PROTOCOL

        def __init__(self, id=None, **kwargs):
            Session.__init__(self, id, **kwargs)

        @classmethod
        def setup(cls, **kwargs):
            """Set up the storage system"""

            db.define_table('cherrypy_sessions',
                            Field('session_id'),
                            Field('locked', 'boolean'),
                            Field('pickled_data', 'blob'),
                            Field('expiration_time', 'datetime'))

        def __del__(self):
            db.commit()

            # Nobody to clean up after us on GAE. We could do it here
            self.clean_up()

        def _exists(self):
            # First check memcache
            data = memcache.get('gae_session_%s' % self.id)
            if data is not None:
                return True

            # Now check datastore
            query = db(
                db.cherrypy_sessions.session_id == self.id)
            record = query.select().first()

            if record is not None:
                # Now that we have retrieved it,
                # let's also cache it!
                session_data = pickle.loads(record.pickled_data)
                expiration_time = record.expiration_time
                memcache.set('gae_session_%s' % self.id,
                             {'data': session_data,
                              'expiration_time': expiration_time})
                return True
            else:
                return False

        def _load(self):
            # First check memcache
            data = memcache.get('gae_session_%s' % self.id)
            if data is not None:
                return data['data'], data['expiration_time']

            # Now check datastore
            query = db(
                db.cherrypy_sessions.session_id == self.id)
            record = query.select().first()

            if record is not None:
                # Now that we have retrieved it,
                # let's also cache it!
                session_data = pickle.loads(record.pickled_data)
                expiration_time = record.expiration_time
                memcache.set('gae_session_%s' % self.id,
                             {'data': session_data,
                              'expiration_time': expiration_time})

                return session_data, expiration_time
            else:
                return None

        def _save(self, expiration_time):
            pickled_data = pickle.dumps(self._data,
                                         self.pickle_protocol)

            db.cherrypy_sessions.update_or_insert(
                db.cherrypy_sessions.session_id == self.id,
                session_id=self.id,
                pickled_data=pickled_data,
                expiration_time=expiration_time)

            db.commit()

            # Now update memcache
            memcache.set('gae_session_%s' % self.id,
                         {'data': self._data,
                          'expiration_time': expiration_time})

        def _delete(self):
            memcache.delete('gae_session_%s' % self.id)
            db(db.cherrypy_sessions.session_id == self.id).delete()
            db.commit()

        def acquire_lock(self):
            """Use memcache for locking. Not ideal, but better than
            nothing.

            """
            delay = 0.1
            while not memcache.add(self.id, "1", namespace='gae_session_lock'):
                time.sleep(delay)
                delay = delay * 2 if delay < 5 else 5
            self.locked = True

        def release_lock(self):
            memcache.delete(self.id, namespace='gae_session_lock')
            self.locked = False

        def clean_up(self):
            """Cleanup expired sessions"""

            db(db.cherrypy_sessions.expiration_time < self.now()).delete()
            db.commit()
