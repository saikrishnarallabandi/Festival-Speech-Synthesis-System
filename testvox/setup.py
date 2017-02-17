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
"""Script to set up development environment as well as full
distributions for direct deployment

This does not currently use distutils.

The main goals of this script are:

(1) After downloading sources, fetch external dependencies and build
them as appropriate.

(2) Create a deployment zipfile that includes all dependencies and
optimized builds of TestVox. This is only for deployment, not useful
for development.

"""

from __future__ import print_function

import argparse
import errno
import os
import re
import shutil
import sys
import subprocess
import tempfile
import urllib
import zipfile

current_dir = os.path.abspath(os.path.dirname(__file__))
testvox_archive_name = 'TestVox-prebuilt'


def check_environment():
    """Check that the environment variables we require have been
    correctly set

    """

    # PYJAMAS_HOME should be set.
    try:
        pyjs_dir = os.environ['PYJAMAS_HOME']
    except KeyError:
        print(''.join([
            'Environment Variable PYJAMAS_HOME missing.\n',
            'Please make it point to where you have ',
            'downloaded PYJAMAS\n(www.pyjs.org)']))
        return False

    # pyjsbuild should be available.
    if not os.path.exists(os.path.join(pyjs_dir,
                                       'bin', 'pyjsbuild')):
        print('pyjsbuild not found')
        print('Please run "python bootstrap.py" in your PYJAMAS directory')
        return False

    # pyjscompress should be available
    if not os.path.exists(os.path.join(pyjs_dir,
                                       'contrib', 'pyjscompressor.py')):
        print('pyjscompress not found')
        print('Make sure you have the latest version of PYJAMAS')
        return False

    return True


def get_dependencies():
    """Download dependencies of the project. This includes:

    (1) Closure compiler to compress HTML/JS output in webclient/
    (2) Cherrypy: the web framework that TestVox uses
    (3) web2py_dal: Data Abstraction Layer from web2py
    (4) PyYAML: For reading config files in YAML format
    (5) Jinja: For templates

    """

    # Create directories if they don't already exist.
    create_directories = [os.path.join(current_dir, x, 'ext_tools')
                          for x in ['webclient', 'webserver']]

    for dirname in create_directories:
        try:
            os.mkdir(dirname)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                # Directory already existed
                pass
            else:
                print('Error creating directory: %s' % dirname)
                print('Could not setup directory structure')
                return False

    if not os.path.exists(os.path.join(current_dir,
                                       'webclient',
                                       'ext_tools',
                                       'compiler.jar')):
        # Download Closure Compiler
        url = ''.join(['http://',
                       'closure-compiler.googlecode.com/',
                       'files/compiler-latest.zip'])

        tmpfile = tempfile.NamedTemporaryFile()
        try:
            print("Downloading Google Closure Compiler...")
            urllib.urlretrieve(url, tmpfile.name)
        except IOError:
            print("Error downloading Google Closure Compiler")
            return False

        try:
            infile = zipfile.ZipFile(tmpfile.name)
        except:
            print("Could not open Google Closure Zip File.")
            return False

        try:
            infile.extract('compiler.jar', os.path.join(current_dir,
                                                         'webclient',
                                                         'ext_tools'))
        except KeyError:
            print("Corrupt Download of Google Closure Compiler")
            return False

    if not os.path.exists(os.path.join(current_dir,
                                       'webserver',
                                       'ext_tools',
                                       'cherrypy.zip')):
        # Download and build deploy-friendly zipfile of cherrypy
        url = ''.join(['http://',
                       'download.cherrypy.org/',
                       'cherrypy/3.2.2/',
                       'CherryPy-3.2.2.zip'])

        tmpfile = tempfile.NamedTemporaryFile()

        try:
            print("Downloading CherryPy")
            urllib.urlretrieve(url, tmpfile.name)
        except IOError:
            print("Error downloading CherryPy")
            return False

        try:
            infile = zipfile.ZipFile(tmpfile.name)
        except:
            print("Could not open CherryPy Zip File.")
            return False

        tmpdir = tempfile.mkdtemp()

        try:
            infile.extractall(tmpdir,
                              [x for x in infile.namelist()
                               if x.startswith('CherryPy')])
        except:
            print("Could not extract CherryPy zipfile.")
            return False

        outfilename = os.path.join(current_dir,
                                       'webserver',
                                       'ext_tools',
                                       'cherrypy.zip')
        print("Creating archive of compiled files")

        with zipfile.PyZipFile(outfilename, mode='w') as zf:
            zf.debug = 0
            zf.writepy(os.path.join(tmpdir, 'CherryPy-3.2.2/cherrypy'))

        print("Creating archive of source files (for GAE)")
        with zipfile.ZipFile(outfilename, mode='a') as zf:
            basepath = 'CherryPy-3.2.2/cherrypy'
            for name in infile.namelist():
                if name.startswith(basepath):
                    if name.endswith('.py') or name.endswith('txt'):
                        arcname = 'cherrypy/%s' % name[len(basepath):]
                        zf.write(os.path.join(tmpdir, name),
                                 arcname=arcname)

        shutil.rmtree(tmpdir)

    if not os.path.exists(os.path.join(current_dir,
                                       'webserver',
                                       'ext_tools',
                                       'yaml.zip')):
        # Download and build deploy-friendly zipfile of PyYAML
        url = ''.join(['http://',
                       'pyyaml.org/download/pyyaml/',
                       'PyYAML-3.10.zip'])

        tmpfile = tempfile.NamedTemporaryFile()

        try:
            print("Downloading PyYAML")
            urllib.urlretrieve(url, tmpfile.name)
        except IOError:
            print("Error downloading PyYAML")
            return False

        try:
            infile = zipfile.ZipFile(tmpfile.name)
        except:
            print("Could not open PyYAML Zip File.")
            return False

        tmpdir = tempfile.mkdtemp()

        try:
            infile.extractall(tmpdir,
                              [x for x in infile.namelist()
                               if x.startswith('PyYAML')])
        except:
            print("Could not extract PyYAML zipfile.")
            return False

        outfilename = os.path.join(current_dir,
                                       'webserver',
                                       'ext_tools',
                                       'yaml.zip')
        print("Creating archive of compiled files")

        with zipfile.PyZipFile(outfilename, mode='w') as zf:
            zf.debug = 0
            zf.writepy(os.path.join(tmpdir, 'PyYAML-3.10/lib/yaml'))

        print("Creating archive of source files (for GAE)")
        with zipfile.ZipFile(outfilename, mode='a') as zf:
            basepath = 'PyYAML-3.10/lib/yaml'
            for name in infile.namelist():
                if name.startswith(basepath):
                    if name.endswith('.py'):
                        arcname = 'yaml/%s' % name[len(basepath):]
                        zf.write(os.path.join(tmpdir, name),
                                 arcname=arcname)
            zf.write(os.path.join(tmpdir, 'PyYAML-3.10', 'LICENSE'),
                     arcname='yaml/LICENSE')

        shutil.rmtree(tmpdir)

    if not os.path.exists(os.path.join(current_dir,
                                       'webserver',
                                       'ext_tools',
                                       'jinja2.zip')):
        # Download and build deploy-friendly zip of jinja2
        url = ''.join(['http://',
                       'github.com/mitsuhiko/',
                       'jinja2/zipball/2.6'])

        tmpfile = tempfile.NamedTemporaryFile()

        try:
            print("Downloading Jinja2")
            urllib.urlretrieve(url, tmpfile.name)
        except IOError:
            print("Error downloading Jinja2")
            return False

        try:
            infile = zipfile.ZipFile(tmpfile.name)
        except:
            print("Could not open Jinja2 Zip File.")
            return False

        tmpdir = tempfile.mkdtemp()

        try:
            infile.extractall(tmpdir,
                              [x for x in infile.namelist()
                               if x.startswith('mitsuhiko-jinja2-abfbc18')])
        except:
            print("Could not extract Jinja2 zipfile.")
            return False

        outfilename = os.path.join(current_dir,
                                       'webserver',
                                       'ext_tools',
                                       'jinja2.zip')
        print("Creating archive of compiled files")

        with zipfile.PyZipFile(outfilename, mode='w') as zf:
            zf.debug = 0
            zf.writepy(os.path.join(tmpdir, 'mitsuhiko-jinja2-abfbc18/jinja2'))

        print("Creating archive of source files (for GAE)")
        with zipfile.ZipFile(outfilename, mode='a') as zf:
            basepath = 'mitsuhiko-jinja2-abfbc18/jinja2'
            for name in infile.namelist():
                if name.startswith(basepath):
                    if name.endswith('.py'):
                        arcname = 'jinja2/%s' % name[len(basepath):]
                        zf.write(os.path.join(tmpdir, name),
                                 arcname=arcname)
            zf.write(os.path.join(tmpdir, 'mitsuhiko-jinja2-abfbc18',
                                  'LICENSE'),
                     arcname='jinja2/LICENSE')

        shutil.rmtree(tmpdir)

    if not os.path.exists(os.path.join(current_dir,
                                       'webserver',
                                       'ext_tools',
                                       'dal.py')):
        # Download Web2Py-DAL
        url = ''.join(['http://',
                       'web2py.googlecode.com/',
                       'hg/gluon/dal.py'])

        outfile = os.path.join(current_dir,
                               'webserver',
                               'ext_tools',
                               'dal.py')
        try:
            print("Downloading Web2Py-DAL...")
            urllib.urlretrieve(url, outfile)
        except IOError:
            print("Error downloading Web2Py-DAL")
            return False

    if not os.path.exists(os.path.join(current_dir,
                                       'webserver',
                                       'ext_tools',
                                       '__init__.py')):
        # Create init file to mark directory as package
        try:
            with open(os.path.join(current_dir,
                                   'webserver',
                                   'ext_tools',
                                   '__init__.py'), 'w') as finit:
                finit.write('')
        except:
            print("Could not create __init__.py")
            return False

    return True


def build(debug=False):
    """We only need to build the webclient in PYJAMAS. Everything on
    the server side is pure python and no build required

    """
    build_dir = os.path.join(current_dir,
                             'webclient',
                             'output')
    build_dir_info_file = os.path.join(build_dir,
                                       '.buildinfo')

    # Check if build type is same as what we are building.
    # If current built is debug, and we want release, we have to
    # clean the output directory and start all over again

    expected_build_type = 'debug' if debug else 'release'

    try:
        with open(build_dir_info_file) as infofile:
            current_build_type = infofile.read()
    except IOError:
        # There's nothing to remove
        current_build_type = expected_build_type

    if current_build_type != expected_build_type:
        print("A different build version exists and will be removed")
        ans = raw_input("Type yes if that's okay: ")
        if ans != 'yes':
            print("Aborting build")
            return False
        shutil.rmtree(build_dir)

    if not os.path.exists(build_dir):
        try:
            os.mkdir(build_dir)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                # Directory already existed
                pass
            else:
                print("Could not create output directory: %s" % build_dir)
                return False
        else:
            # Save the current build info in file
            with open(build_dir_info_file, 'w+') as infofile:
                infofile.write(expected_build_type)

    # Run the command to build output!
    cmd = ['python',
           os.path.join(os.environ['PYJAMAS_HOME'],
                        'bin', 'pyjsbuild'),
           '--enable-strict',
           '--enable-debug' if debug else '--disable-debug',
           '--dynamic-link',
           '--enable-signatures',
           '--output=%s' % build_dir,
           'testvox_client']
    working_dir = os.path.join(current_dir,
                               'webclient', 'src')

    try:
        process = subprocess.Popen(' '.join(cmd),
                                   shell=True,
                                   cwd=working_dir)
        process.wait()
    except:
        print("Could not build webclient")
        return False

    if not debug:
        # We must compress the created output
        cmd = ['python',
               os.path.join(os.environ['PYJAMAS_HOME'],
                        'contrib', 'pyjscompressor.py'),
               build_dir,
               '-c',
               os.path.join(current_dir,
                            'webclient', 'ext_tools',
                            'compiler.jar'),
               '-j', '0',
        ]
        try:
            process = subprocess.Popen(' '.join(cmd),
                                       shell=True)
            process.wait()
        except:
            print("Could not compress webclient output")
            return False

    return True


def deploy():
    """Create a zipfile that others can use as "installed" version of
    TestVox: Ready to run by simply unzipping

    """

    # Create the zipfile first
    try:
        zf = zipfile.ZipFile(os.path.join(current_dir,
                                          '%s.zip' % testvox_archive_name),
                             'w', zipfile.ZIP_DEFLATED)
    except:
        print("Could not create output file")
        return False

    for dirpath, dirnames, filenames in os.walk('webserver',
                                                followlinks=True):
        if dirpath == 'webserver':
            try:
                dirnames.remove('gen')
            except ValueError:
                # gen was not created
                pass
        for f in filenames[:]:
            if f.startswith('.') or f.endswith('.pyc'):
                filenames.remove(f)

        # Pyjamas creates files with md5 signatures. If a file has
        # both signature and non-signature versions, remove the
        # non-signature version
        for name in filenames[:]:
            tokens = name.split('.')
            # The second-last item is the md5 sum
            md5token = tokens[-2]
            if re.findall(r"([a-fA-F\d]{32})", md5token):
                # Seems like a valid md5 token
                del tokens[-2]
                newname = '.'.join(tokens)
                if newname in filenames:
                    filenames.remove(newname)

        # Replace webserver with archive_name in path
        archive_dirpath = testvox_archive_name + dirpath[len('webserver'):]
        zf.write(dirpath, archive_dirpath)

        # Add Files
        for f in filenames:
            zf.write(os.path.join(dirpath, f),
                     os.path.join(archive_dirpath, f))
            print("Adding: %s" % os.path.join(archive_dirpath, f))

    # Add text files
    for f in ['README.rst', 'LICENSE']:
        zf.write(os.path.join(current_dir, f),
                 os.path.join(testvox_archive_name, f))

    # Add scripts directory
    for dirpath, dirnames, filenames in os.walk('scripts'):
        archive_dirpath = os.path.join(testvox_archive_name, dirpath)
        zf.write(dirpath, archive_dirpath)
        for f in filenames:
            if f.endswith('.py'):
                zf.write(os.path.join(dirpath, f),
                         os.path.join(archive_dirpath, f))

    # Add contrib directory
    for dirpath, dirnames, filenames in os.walk('contrib'):
        archive_dirpath = os.path.join(testvox_archive_name, dirpath)
        zf.write(dirpath, archive_dirpath)
        for f in filenames:
            zf.write(os.path.join(dirpath, f),
                     os.path.join(archive_dirpath, f))
    zf.close()


def clean_dist():
    """Clean source distribution. Remove all non-source data"""
    print("All built directories, data stored by server will be deleted!")
    ans = raw_input("Type yes if sure: ")
    if ans != 'yes':
        print("Cancelling clean_dist")
        return False

    remove_dirs = [os.path.join(current_dir, 'webclient', 'output'),
                   os.path.join(current_dir, 'webclient', 'ext_tools'),
                   os.path.join(current_dir, 'webserver', 'ext_tools'),
                   os.path.join(current_dir, 'webserver', 'gen')]

    for dirname in remove_dirs:
        try:
            shutil.rmtree(dirname)
        except OSError as exc:
            if exc.errno == errno.ENOENT:
                pass
            else:
                print("Failed to delete %s" % dirname)
                return False

    # Also remove deployment version, if any.
    try:
        os.remove('%s.zip' % testvox_archive_name)
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            # File did not exist
            pass
        else:
            print("Could not remove deployed archive")
            return False

    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Script to setup TestVox')
    parser.add_argument('--task', default='build_debug',
                        choices=['get_dependencies',
                                 'build_debug',
                                 'build_release',
                                 'clean_dist',
                                 'deploy'],
)
    args = parser.parse_args()

    def ensure(func):
        if not func():
            print("Setup Failed. Aborting")
            sys.exit(1)

    if args.task == 'get_dependencies':
        ensure(check_environment)
        ensure(get_dependencies)
    elif args.task == 'build_debug':
        ensure(check_environment)
        ensure(get_dependencies)
        build(debug=True)
    elif args.task == 'build_release':
        ensure(check_environment)
        ensure(get_dependencies)
        build(debug=False)
    elif args.task == 'clean_dist':
        ensure(clean_dist)
    elif args.task == 'deploy':
        ensure(check_environment)
        ensure(get_dependencies)
        ensure(build)
        deploy()
