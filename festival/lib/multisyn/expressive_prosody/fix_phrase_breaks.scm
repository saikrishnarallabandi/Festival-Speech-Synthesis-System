
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
(define (fix_phrase_breaks utt)
  "(fix_phrase_breaks UTT)

If Phrase_Method is prob_models, the ngram apparently does not look at 
punctuation at all, at least it cannot detect sentence-ending punctuation
combined with (single or double) quotes.

fix_phrase_breaks will set pbreak to BB at any sentence-final position
(punctuation contains [.:?!] -- note that periods are removed by text 
normalization when followed by a blank and a lower case character).

30 Oct 2006: comma and semicolon added.

"
(let (word tword token lword punc)
   (set! word (utt.relation.first utt 'Word))

   (while word
      (set! word_name (item.name word))

      (set! tword (item.relation word 'Token))
      (set! token (item.parent tword))
      (set! lword (item.daughtern token))
      (while (equal? "punc" (item.feat lword 'pos))
         (set! lword (item.prev lword)))

      (set! punc (item.feat token 'punc))

      (if(equal? tword lword)
       (begin
         ; (format t "fix_phrase_breaks: %s %s %s\n" 
         ;         word_name punc (item.feat word 'pbreak))
         (if(string-matches punc ".*[,;.:?!].*")
            (if(not(equal? "BB" (item.feat word 'pbreak)))
               (begin
                  (format t "fix_phrase_breaks: at \"%s\": %s -> BB because %s\n"
                            word_name (item.feat word 'pbreak) punc)
                  (item.set_feat word 'pbreak "BB")))
            (if(not(equal? "NB" (item.feat word 'pbreak)))
               (begin
                  (format t "fix_phrase_breaks: at \"%s\": %s -> NB\n"
                            word_name (item.feat word 'pbreak))
                  (item.set_feat word 'pbreak "NB"))))))
      (set! word (item.next word)))))


(provide 'fix_phrase_breaks)
