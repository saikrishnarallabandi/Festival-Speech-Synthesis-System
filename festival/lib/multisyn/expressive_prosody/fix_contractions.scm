
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

(define (fix_contractions utt)
  "(fix_contractions UTT)

The apostroph in the contractions like he'll is lost in the word relation
i.e. the word becomes hell which is pronounced differently.  Since 
(Word utt) always picks the first variant (no matter what the guessed POS 
is,  which is wrong anyway) the apostrophes for the following contractions

   he'll, i'd, i'll, she'd, she'll, we'd, we're, and d'art

are put back into the names in the word relation, therefore this function 
should be called before (Word utt).

Of course these contractions need to be added to the lexicon addendum. 
See the comments in the module containing this definition for how to 
do this for unilex-rpx and unilex-edi.



"
(let(token token_name replacement)
   (set! token (utt.relation.first utt 'Token))
   (while token
      (set! token_name (item.name token))
      (set! replacement "")
      (if(string-matches token_name  ".*\'.*")
         (cond
            ((or(equal? token_name "He\'ll")(equal? token_name "he\'ll"))
                   (set! replacement "he\'ll"))
            ((or(equal? token_name "I\'d")(equal? token_name "i\'d"))
                   (set! replacement "i\'d"))
            ((or(equal? token_name "I\'ll")(equal? token_name "i\'ll"))
                   (set! replacement "i\'ll"))
            ((or(equal? token_name "He\'d")(equal? token_name "he\'d"))
                   (set! replacement "i\'ll"))
            ((or(equal? token_name "He\'ll")(equal? token_name "he\'ll"))
                   (set! replacement "he\'ll"))
            ((or(equal? token_name "She\'d")(equal? token_name "she\'d"))
                   (set! replacement "she\'d"))
            ((or(equal? token_name "She\'ll")(equal? token_name "she\'ll"))
                   (set! replacement "she\'ll"))
            ((or(equal? token_name "We\'d")(equal? token_name "we\'d"))
                   (set! replacement "we\'d"))
            ((or(equal? token_name "We\'ll")(equal? token_name "we\'ll"))
                   (set! replacement "we\'ll"))
            ((or(equal? token_name "We\'re")(equal? token_name "we\'re"))
                   (set! replacement "we\'re"))
            ((or(equal? token_name "D\'art")(equal? token_name "d\'art"))
                   (set! replacement "d\'art"))))
      (if(not(equal? replacement ""))
         (begin
            (set! word (item.daughter1 token))
            (if(equal?(item.feat word 'pos) "punc")
               (set! word (item.next word)))
            (item.set_name word replacement)
            (format t "fix_contractions: word set to %s\n" replacement)))

      (set! token (item.next token)))))

; Add this to "unilex-rpx.scm":
; in Festvox/festival/lib/dicts/unilex
;
; (lex.add.entry '("he\'ll" nil(((h ii lw) 1))))
; (lex.add.entry '("i\'d"   nil(((ai d) 1))))
; (lex.add.entry '("i\'ll"  nil(((ai lw) 1))))
; (lex.add.entry '("she\'d" nil(((sh ii d) 1))))
; (lex.add.entry '("she\'ll"nil(((sh ii lw) 1))))
; (lex.add.entry '("we\'d"  nil(((w ii d) 1))))
; (lex.add.entry '("we\'ll" nil(((w ii lw) 1))))
; (lex.add.entry '("we\'re" nil(((w i@ r) 1))))
; (lex.add.entry '("d\'art" nil (((d aa) 1))))
;
; and this to "unilex-edi-simplyfied.scm":
;
; (lex.add.entry '("he\'ll"  nil (((h ii l) 1)))) 
; (lex.add.entry '("i\'d"    nil (((ai d) 1)))) 
; (lex.add.entry '("i\'ll"   nil (((ai l) 1)))) 
; (lex.add.entry '("she\'d"  nil (((sh ii d) 1)))) 
; (lex.add.entry '("she\'ll" nil (((sh ii l) 1)))) 
; (lex.add.entry '("we\'d"   nil (((w ii d) 1)))) 
; (lex.add.entry '("we\'ll"  nil (((w ii l) 1)))) 
; (lex.add.entry '("we\'re"  nil (((w ii r) 1)))) 
; (lex.add.entry '("d\'art" nil (((d a) 1))))
;
; and this to "unilex-edi-full.scm":
;
; (lex.add.entry '("he\'ll"  nil (((h iii l) 1))) 
; (lex.add.entry '("i\'d"    nil (((ae d) 1))) 
; (lex.add.entry '("i\'ll"   nil (((ae l) 1))) 
; (lex.add.entry '("she\'d"  nil (((sh iii d) 1))) 
; (lex.add.entry '("she\'ll" nil (((sh iii l) 1))) 
; (lex.add.entry '("we\'d"   nil (((w iii d) 1))) 
; (lex.add.entry '("we\'ll"  nil (((w iii l) 1))) 
; (lex.add.entry '("we\'re"  nil (((w ir r) 1))) 
; (lex.add.entry '("d\'art" nil (((d a) 1))))


(provide 'fix_contractions)
