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
"""Generate file with HTTP DIGEST auth access details for admin"""

import getpass
import hashlib
import os
import sys


def get_ha1(user, realm, password):
    """Compute the HA1"""
    s = ':'.join([user, realm, password])
    return hashlib.md5(s).hexdigest()


if __name__ == '__main__':
    realm = 'TestVox Administration'
    rand = os.urandom(65536)
    key = hashlib.sha512(rand).hexdigest()

    user = raw_input("Username: ")
    password = getpass.getpass("Password: ")
    password2 = getpass.getpass(" Confirm: ")
    if password != password2:
        print("Password mismatch")
        print("Aborting")
        sys.exit(1)

    ha1 = get_ha1(user, realm, password)

    text = '\n'.join(
        ['"""This file is auto-generated. Do not modify"""',
         'realm = "%s"' % realm,
         'user_ha1dict = {"%s": "%s"}' % (user, ha1),
         'get_ha1 = lambda r, u: user_ha1dict[u] if u in user_ha1dict else ""',
         'digest_key = "%s"' % key,
         ''
         ])

    # Find out where to save the file
    current_dir = os.path.abspath(os.path.dirname(__file__))
    path_src = os.path.join(current_dir,
                            '..', 'webserver', 'controllers')
    path_prebuilt = os.path.join(current_dir, '..',
                                 'controllers')
    if os.path.exists(path_src):
        outfile = os.path.join(path_src, 'gen_auth.py')
    elif os.path.exists(path_prebuilt):
        outfile = os.path.join(path_prebuilt, 'gen_auth.py')
    else:
        print("Couldn't determine location of gen_auth.py")
        sys.exit(1)

    with open(outfile, "w") as fout:
        fout.write(text)
