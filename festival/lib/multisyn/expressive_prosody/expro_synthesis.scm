
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
;;;  Maybe inventing a few new hooks in ../../synthesis would be cleaner
;;;  than re-defining (Text UTT) and (Word UTT).


(require 'fix_contractions)
(require 'fix_phrase_breaks)
(require 'detect_quoting)
(require 'expro_emphasis)
(require 'boundary_tones)
(require 'star_accent)
(require 'expro_target_cost)


(set! DocText (doc Text))
(set! DocWord (doc Word))


(set! OrigText Text)
(define (Text utt)
   (if(symbol-bound? 'debug-expro)(format t "OrigText\n"))
   (OrigText utt)
   (if(symbol-bound? 'debug-expro)(format t "star_accent_token\n"))
   (star_accent_token utt))

   
(set! DocText (string-append DocText 
                             "\n\n Re-defined by expro_synthesis as:\n\n"
                             "(Text utt)\n"
                             "(star_accent_token utt)"))

(set! OrigWord Word)
(define (Word utt)
   (if(symbol-bound? 'debug-expro)(format t "fix_contractions\n"))
   (fix_contractions utt)
   (if(symbol-bound? 'debug-expro)(format t "fix_phrase_breaks\n"))
   (fix_phrase_breaks utt)
   (if(symbol-bound? 'debug-expro)(format t "OrigWord\n"))
   (OrigWord utt)
   (if(symbol-bound? 'debug-expro)(format t "star_accent_syllable\n"))
   (star_accent_syllable utt)
   (if(symbol-bound? 'debug-expro)(format t "detect_quoting\n"))
   (detect_quoting utt t)
   (if(symbol-bound? 'debug-expro)(format t "expro_emphasis\n"))
   (expro_emphasis utt)
   (if(symbol-bound? 'debug-expro)(format t "boundary_tones\n"))
   (boundary_tones utt))

(set! DocWord (string-append DocWord
                             "\n\n Re-defined by expro_synthesis as:\n\n"
                             "(fix_contractions utt)\n"
                             "(fix_phrase_breaks utt)\n"
                             "(Word utt)\n"
                             "(detect_quoting utt t)\n"
                             "(expro_emphasis utt)\n"
                             "(boundary_tones utt)\n"
                             "(star_accent_syllable utt)\n"))

(add-doc-var 'Text DocText)
(add-doc-var 'Word DocWord)


(provide 'expro_synthesis)
