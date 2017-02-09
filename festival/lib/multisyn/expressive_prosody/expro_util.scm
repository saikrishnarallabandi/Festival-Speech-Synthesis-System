
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


(define (apply_to_utts procedure uttlist)
"(apply_to_utts PROCEDURE UTTLIST)

Load each utterance, apply PROCEDURE, and save the utterance back.
UTTLIST is a list of utterance names without the .utt extension,
PROCEDURE should expect one argument: the utterance (not its name).

"

(mapcar
   (lambda uttname
      (set! uttname (format nil "%s.utt" (car uttname)))
      (set! u (utt.load nil uttname))
      (procedure u)
      (utt.save u uttname)
      (format t "%s done\n" uttname))
   uttlist))



(define (fabs x)
"(fabs x)  just what you expect
"
(if (> x 0) x (- 0 x)))

(define (item.relation.Parent ITEM RELATION)
"(item.relation.Parent ITEM RELATION)

Just as (item.relation.parent ITEM RELATION), but returns nil if ITEM is nil.
"
(if ITEM
   (item.relation.parent ITEM RELATION)
   nil))

(define (item.Parent ITEM)
"(item.Parent ITEM)

Just as (item.parent ITEM), but returns nil if ITEM is nil.
"
(if ITEM
   (item.parent ITEM)
   nil))


(define (current_lex)
"(current_lex)
 
 Returns the name of the current lexicon.
"
(let(first_lex cur_lex)
   (set! first_lex (car(lex.list)))
   (if(not first_lex)
      (error "(lex.list) is empty, cannot determine current_lex"))
   (set! cur_lex (lex.select first_lex))
   (lex.select cur_lex)
   cur_lex
))


(provide 'expro_util)
