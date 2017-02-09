
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;                                                                       ;;
;;;                Centre for Speech Technology Research                  ;;
;;;                     University of Edinburgh, UK                       ;;
;;;                       Copyright (c) 2005, 2006                        ;;
;;;                        All Rights Reserved.                           ;;
;;;                                                                       ;;
;;;  Permission is hereby granted, free of charge, to use and distribute  ;;
;;;  this software and its documentation without restriction, including   ;;
;;;  without limitation the rights to use, copy, modify, merge, publish,  ;;
;;;  distribute, sublicense, and/or sell copies of this work, and to      ;;
;;;  permit persons to whom this work is furnished to do so, subject to   ;;
;;;  the following conditions:                                            ;;
;;;   1. The code must retain the above copyright notice, this list of    ;;
;;;      conditions and the following disclaimer.                         ;;
;;;   2. Any modifications must be clearly marked as such.                ;;
;;;   3. Original authors' names are not deleted.                         ;;
;;;   4. The authors' names are not used to endorse or promote products   ;;
;;;      derived from this software without specific prior written        ;;
;;;      permission.                                                      ;;
;;;                                                                       ;;
;;;  THE UNIVERSITY OF EDINBURGH AND THE CONTRIBUTORS TO THIS WORK        ;;
;;;  DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING      ;;
;;;  ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT   ;;
;;;  SHALL THE UNIVERSITY OF EDINBURGH NOR THE CONTRIBUTORS BE LIABLE     ;;
;;;  FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES    ;;
;;;  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN   ;;
;;;  AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,          ;;
;;;  ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF       ;;
;;;  THIS SOFTWARE.                                                       ;;
;;;                                                                       ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;
;;;  Author: Volker Strom
;;;


(define (expro_emphasis utt)
"(expro_emphasis utt)

Set a segment feature 'emph to 1 based on quotation
marks (token features squoted, dquoted, upcased, see
(detect_quoting utt)) and whether 'punc contains an
exclamation mark.  Only segments on stressed syllables 
get the emph feature.

This is somewhat specific to the Carroll part of the 
Roger voice.

2007-02-06: Also overwrites the syllable feature 'accented
and the segment feature 'star_accent:

        syl is          seg is
       accented     emph    star_accent
AHEM     0  2       0  1     0  1
AHEM@    0  2       0  1     0  1
ahem*   -1  1       0  0     0  1
ahem+   -1  0.5     0  0     0  0.5
ahem    -1  0       0  0     0  0
ahem@   -1 -1       0  0    -1 -1

"

(let (token squoted dquoted upcased word firstwordinsentence)
   (set! token (utt.relation.first utt 'Token))
   (while token
   
      (set! squoted (item.feat token 'squoted))
      (set! dquoted (item.feat token 'dquoted))
      (set! upcased (item.feat token 'upcased))
      (set! firstwordinsentence nil)

      (if(not(item.prev token))
         (set! firstwordinsentence t)
         (if(string-matches (item.feat (item.prev token) 'punc) ".*[.:?!].*")
            (begin;(format t "%s is firstwordinsentence\n" (item.name token))
            (set! firstwordinsentence t))))
   
      ;(format t "%s\t%d %d %d %s\n" (item.name token) squoted dquoted upcased
      ;       (item.feat token 'punc))
   
      ;; In the Carroll subcorpus, single quotes are used for ordinary quotations,
      ;; double quotes for quotes within quotes, which Roger read more prominent,
      ;; when they are 1 or 2 words long.  1 or 2 uppercased words in a row are 
      ;; also prominent, as well as ordinary quotations of length one or length
      ;; two but folloed by an exclamation mark.  
      ;; Finally, one-word sentences having an exclamation mark are also 
      ;; prominent.  This is specific to the Unilex subcorpus.  This last rule 
      ;; makes expro_emphasis_unilex obsolete.
      (if(or(and(<= dquoted 2)(> dquoted 0))
            (and(<= upcased 2)(> upcased 0))
            (and(<= squoted 1)(> squoted 0))
            (and(<= squoted 2)(> squoted 0)
                (string-matches (item.feat token 'punc) ".*!.*"))
            (and firstwordinsentence
                (string-matches (item.feat token 'punc) ".*!.*")))
         (begin
            (format t "set emphasis\n")
            (mapcar
               (lambda(word)
                 (set! word (item.relation word 'SylStructure))
                 (if word
                   (if(not(string-equal "punc" (item.feat word 'pos)))
                      (begin
                         (format t "\tto word %s\n" (item.name word))
                         (mapcar
                            (lambda(syl)
                               (if(equal? 1 (item.feat syl 'stress))
                                  (begin
                                     (item.set_feat syl 'accented 2)
                                     (mapcar
                                        (lambda(seg)
                                           (begin
                                              (item.set_feat seg 'star_accent 1)
                                              (item.set_feat seg 'emph 1)))
                                        (item.daughters syl)))
                                   (item.set_feat syl 'accented 0)))
                            (item.daughters word))))))
               (item.leafs token))))
   
      (set! token (item.next token)))))



(define (expro_emphasis_unilex utt)
"(expro_emphasis_unilex utt)

Foreach segment that belongs to a stressed syllable AND belongs 
to a token whose 'punc feature contains an exclamation mark, set 
a segment feature 'emph to 1.
This is specific to the unilex and spelling subcorpora of the 
Roger voice.

"
(let (token)
   (set! token (utt.relation.first utt 'Token))
   (while token
   
      ;(format t "%s\t%s\n" (item.name token)
      ;       (item.feat token 'punc))
   
      (if(string-matches (item.feat token 'punc) ".*!.*")
         (begin
            (mapcar
               (lambda(word)
                  (set! word (item.relation word 'SylStructure))
                  (if(not(string-equal "punc" (item.feat word 'pos)))
                     (begin
                        (format t "\tto word %s\n" (item.name word))
                        (mapcar
                           (lambda(syl)
                              (if(equal? 1 (item.feat syl 'stress))
                                 (mapcar
                                    (lambda(seg)
                                       (item.set_feat seg 'emph 1))
                                    (item.daughters syl))))
                           (item.daughters word)))))
               (item.leafs token))))
   
      (set! token (item.next token)))))


(provide 'expro_emphasis)

