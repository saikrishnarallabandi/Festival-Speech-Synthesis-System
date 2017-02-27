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
"""
Downloads and creates a zip-importable version of the boto package
"""
import os
import tempfile
import urllib
import shutil
import sys
import zipfile


if __name__ == '__main__':
    boto_package_file = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'boto.zip')

    if not os.path.exists(boto_package_file):
        # Download and build a .zip package of boto
        print("Downloading Package Boto")

        url = ''.join(['http://',
                       'github.com/boto/boto/zipball/2.5.2'])

        tmpfile = tempfile.NamedTemporaryFile()

        try:
            urllib.urlretrieve(url, tmpfile.name)
        except IOError:
            print("Error downloading Boto")
            sys.exit(1)

        try:
            infile = zipfile.ZipFile(tmpfile.name)
        except:
            print("Could not open Boto Zip File.")
            sys.exit(1)

        tmpdir = tempfile.mkdtemp()

        try:
            infile.extractall(tmpdir,
                              [x for x in infile.namelist()
                               if x.startswith('boto-boto-f72c829')])
        except:
            print("Could not extract Boto zipfile.")
            sys.exit(1)

        print("Creating boto archive")

        with zipfile.PyZipFile(boto_package_file, mode='w') as zf:
            zf.debug = 0
            zf.writepy(os.path.join(tmpdir, 'boto-boto-f72c829/boto'))
        shutil.rmtree(tmpdir)
        print("Success")
    else:
        print("Boto already downloaded")
