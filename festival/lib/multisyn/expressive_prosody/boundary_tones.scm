
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

(define (fix_utterance_final_punc utt)
"
(fix_utterance_final_punc UTT)

When an utterance ends in something that could be considered an 
abbreviation, e.g. 'Say A or B.', the 'punc feature of the 
utterance-final token is '0' (as a string).  To be on the safe side,
if this feature is 0 (either as a string or a number), put all
utterance-final characters from (utt.feat utt 'iform) which are not 
letters into that 'punc feature.

"
(let (last_token iform i punc c)
   (set! last_token (utt.relation.last utt 'Token))
   (if(or(string-equal "0" (item.feat last_token 'punc))
         (equal? 0 (item.feat last_token 'punc)))
      (begin
         (set! iform (utt.feat utt 'iform))
         (set! i (- (string-length iform) 2))
         (set! punc "")
         (while (> i 0)
             (set! c (substring iform i 1))
             (if (string-matches c "[a-zA-Z]")
                (set! i 0) ; leave the loop when the first letter is found
                (begin     ; else consider char as part of utterance-final punc
                   (if(not(string-equal " " c))
                      (set! punc (string-append c punc)))
                   (set! i (- i 1)))))
            (if (string-equal punc "")
               (set! punc "."))
            (item.set_feat last_token 'punc punc)
            (format t "fix_utterance_final_punc: utterance_final_punc set to %s\n"
                    punc)))))


(define (set_btone word_item btone)
"(set_btone word_item btone)

Set boundary tone feature 'btone in each segement of the word-final syllable.
"
(let (w ls)
   (set! w (item.relation word_item 'SylStructure))
   ;;!(format t "\tset_btone: %s to word %s\n" btone (item.name w))
   (set! ls (item.daughtern w)) ;word-final syllable
   (mapcar
      (lambda pho
         (begin
            ;;!(format t "\t\tset_btone: to %s\n" (item.name(car pho)))
            (item.set_feat (car pho) "btone" btone)))
      (item.leafs ls))))


;; boundary_tones still gets fooled by:
;;
;; However, what about the parents...
;; So what happened?
;; But how?
;; And how did it end up...
;; I mean, who do they think they are?
;; If it was a political decision, who was responsible?

(define (boundary_tones utt)
  "(boundary_tones UTT)

Set the feature 'btone in segment in word-final syllables:
* 'I'  (for interrogative) at the end of yes/no-questions or,
       in alternative questions, at the end of each alternative
       but the last one (ending with a comma, followed by the 
       word 'or').  Yes/no-questions end in '?' and do not 
       start with an interrogative pronoun (POS is either 'wp' 
       or 'wrb' or 'wdt').
* 'T'  (for terminal) at the end of all other types of sentences
       (punctuation contains [.:?!])
* 'C'  (for continuation rise) if a word ends in [,;] (alternaitve
       questions exempt, see 'I')
  
The text normalization currently cannot properly handle most types 
of contractions, e.g. \"What'll\", and in turn the POS tagger does 
not tag it as a 'wp'  (\"What's\" on the other hand does work).

"

(fix_utterance_final_punc utt)

(let ((sentence_initial t)
      (yn_question nil)
      (contains_or nil)
      (end_of_alternatives nil)
      word word_name tword token lword punc)

   (set! word (utt.relation.first utt 'Word))

   (while word
      (set! word_name (item.name word))

      (set! tword (item.relation word 'Token))
      (set! token (item.parent tword))
      (set! lword (item.daughtern token))
      (while (equal? "punc" (item.feat lword 'pos))
         (set! lword (item.prev lword)))

      (set! punc (item.feat token 'punc))

      ;;!(format t "boundary_tones: %s\n" word_name);

      (if sentence_initial
         (begin
            ;;!(format t "boundary_tones: sentence initial %s, pos %s\n"
            ;;!           word_name (item.feat word 'pos))
            (if(not(string-matches (item.feat word 'pos) "w.*"))
               (set! yn_question t)) ; tentatively, depends on sent-final punc
            (set! sentence_initial nil)))
            

      (if(equal? tword lword) ; the rest applies for token-final words only
      ; We could as well loop over tokens in the first place, but my plan
      ; is to fix the handling of contractions: tokens like "What's" will
      ; then be split into the words "what" and "'s".
       (begin
         ;;!(format t "boundary_tones: token-final %s %s\n" word_name punc)
         (if(string-matches punc ".*[.?!].*")
            (begin
               ;;!(format t "sentence final\n")
               (if(and(string-matches punc ".*[?].*")
                      yn_question)
                  (if contains_or
                     (begin
                        ;;!(format t "\tALTERNATIVE QUESTION\n")
                        (set_btone word "T")
                        (mapcar
                           (lambda(w)
                              ;;!(format t "\t\tALT: %s\n" (item.name w))
                              (set_btone w "I"))
                           end_of_alternatives))
                     (begin
                        ;;!(format t "\tINTERROGATIVE\n")
                        (set_btone word "I")))
                  (begin
                     ;;!(format t "\tTERMINAL\n")
                     (set_btone word "T")))
               (set! sentence_initial t)
               (set! yn_question nil)
               (set! contains_or nil)
               (set! end_of_alternatives nil))
            (if(string-matches punc ".*[,;:].*")
               (begin
                  ;;!(format t "\tCONTINUATION\n")
                  (set_btone word "C")
                  ;;; Keep a list of all Cs in order to change them to Is
                  ;;; if this sentence turns out to be an alt. _question_,
                  (set! end_of_alternatives
                        (append end_of_alternatives (list word)))
                  (if(and(item.next word)
                         (string-equal "or" (item.name(item.next word))))
                     (begin
                        ;;!(format t "\tALTERNATIVE\n")
                        (set! contains_or t)))))))) 
      (set! word (item.next word)))))


(provide 'boundary_tones)
