###########################################################################
##                                                                       ##
##                   Carnegie Mellon University                          ##
##                         Copyright (c) 2003                            ##
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
##  The CMU_ARCTIC databases                                             ##
##    General phonetically rich synthesis databases in US English        ##
##                                                                       ##
##  John Kominek, Alan W Black                                           ##
##  Language Technologies Institute                                      ##
##  Carnegie Mellon University                                           ##
##                                                                       ##
###########################################################################
TOP=../..
DIRNAME=festvox.org/cmu_arctic
BUILD_DIRS = 
ALL_DIRS = 
HTMLBODIES= index_body.html dbs_awb_body.html dbs_jmk_body.html \
            dbs_bdl_body.html dbs_slt_body.html \
            dbs_rms_body.html dbs_clb_body.html \
            dbs_ksp_body.html
HTMLBITS= sidebar.html
FINALHTML= $(HTMLBODIES:_body.html=.html)
PERL= 
OTHERS = 
FILES = Makefile $(HTMLBODIES) $(HTMLBITS) $(PERL) $(OTHERS)

ALL = $(FINALHTML)

LOCAL_CLEAN = $(FINALHTML) *.tmp.html

include $(TOP)/config/common_make_rules

%.html : %_body.html $(HTMLBITS) ../header.html ../footer.html ../make_html
	@ ../make_html $< "../" ../header.html ../footer.html sidebar.html >$@

install:
	scp -p $(FINALHTML) ../../src/vox_files/prompts/cmuarctic.data festvox.org:websites/www.festvox.org/html/cmu_arctic
#	scp -p $(PERL) token.metronomicon.com:websiteswww.festvox.org/cgi-bin


