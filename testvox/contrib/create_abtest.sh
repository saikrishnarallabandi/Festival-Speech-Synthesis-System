#!/bin/bash
###########################################################################
##                                                                       ##
##                  Language Technologies Institute                      ##
##                     Carnegie Mellon University                        ##
##                         Copyright (c) 2013                            ##
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
##  Date  : June 2013                                                    ##
###########################################################################
#
# Take two directories and create an A-B test zipfile for use in TestVox
#

if [ $# != 3 ]
then
	echo "Usage: $0 a-dir b-dir name.zip"
	echo "a-dir and b-dir must have the all the same files, in wav format"
	exit 1
fi

# Check that a-dir, b-dir exist, and name.zip doesn't.
if [ ! -d $1 ]
then
	echo "a-dir $1 doesn't exist"
	exit 1
fi
if [ ! -d $2 ]
then
	echo "b-dir $2 doesn't exist"
	exit 1
fi
if [ -e $3 ]
then
	echo "output $3 already exists"
	exit 1
fi

# Check that a-dir and b-dir have exactly the same (and non-zero #) of wav files
alist=$(ls -1 $1/*.wav)
blist=$(ls -1 $2/*.wav)
if [ -z "$alist" ]
then
	echo "You need at least one wavfile to run abtest"
	exit 1
fi

if [ "$alist" != "$blist" ]
then
        echo $alist $blist
	echo "a-dir and b-dir must have exactly the same files"
	exit 1
fi

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

mkdir -p $TMPDIR/mp3

outdira=$(basename $1)
outdirb=$(basename $2)

mkdir -p $TMPDIR/mp3/$outdira
mkdir -p $TMPDIR/mp3/$outdirb

for i in $alist
do
	name=$(basename $i .wav)
	lame -V1 $i $TMPDIR/mp3/$outdira/$name.mp3
done

for i in $blist
do
	name=$(basename $i .wav)
	lame -V1 $i $TMPDIR/mp3/$outdirb/$name.mp3
done

echo "
testvox_config:
  base_media_directory: mp3
  pagetitle: A/B Preference Task

testvox_steps:
  - name: listening_task
    task_type: abtask

    instruction: >-
      Listen to the two audio clips below, and 
      tell us which one you prefer.

    directory_a: $outdira
    directory_b: $outdirb
    ab_randomize: Yes  # Randomize order of A-clip and B-clip presented to participants
    audio_autoplay: No
    data_randomize: Yes  # Present the different data files in random order

    data:" > $TMPDIR/config.yaml

for i in $alist
do
	echo "      - filename: $(basename $i .wav).mp3"
done >> $TMPDIR/config.yaml

cat $TMPDIR/config.yaml


python $(dirname $0)/../scripts/create_experiment_zipfile.py $TMPDIR $3




