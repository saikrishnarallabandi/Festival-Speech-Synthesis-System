
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

(define (star_accent_token utt)
"(star_accent_token UTT)

For each token marked up with a star, set token feature 'star_accent
to 1 and remove the star from the token name.  Secondary accent may
be marked up with a plus sign; feature 'star_accent then is 0.5.
De-accented tokens may be marked up with the at sign @; feature 
'star_accent then is -1.

This function should be called before (Token UTT), which makes words 
from tokens.

Once there are syllables, call (star_accent_syllable utt) to bequeath
the star_accent feature down to the segments of the lexically 
stressed syllable, for more efficiency.

Since 2007-02-06 the 'star_accent feature of segments is also available
as feature 'accented of syllables.
"
(let (token token_name i cleanword c)
   (set! token (utt.relation.first utt 'Token))
   (while token
      (set! token_name (item.name token))
      ;;(format t "token name is %l\n" token_name)
      (set! i (- (string-length token_name) 1))
      (set! cleanword "")
      (while (>= i 0)
         (set! c (substring token_name i 1))
         ;;(format t "\t%s\n" c)
         (if (string-equal c "\*")
            (item.set_feat token 'star_accent 1)
            (if (string-equal c "\+")
               (item.set_feat token 'star_accent 0.5)
               (if (string-equal c "@")
                  (item.set_feat token 'star_accent -1)
                  (set! cleanword (string-append c cleanword)))))
         (set! i (- i 1)))
      (item.set_feat token 'name cleanword)
      (set! token (item.next token)))))


(define (star_accent_syllable utt)
"(star_accent_syllable UTT)

Bequeath the 'star_accent feature, if there is any, from token
items to the segments of the primary lexically stressed syllable. 
If a there more than one word for a token, all are treated 
equally (may the rightmost only should get it).

Since 2007-02-06 the 'star_accent feature of segments is also available
as feature 'accented of syllables.
"

(let (token token_name)
   (set! token (utt.relation.first utt 'Token))
   (while token
      (set! token_name (item.name token))
      ;;(format t "token name is %l\n" token_name)
      (if(not(equal? 0 (item.feat token 'star_accent)))
         (mapcar
            (lambda(w)
               ;;(format t "\tword name is %l\n" (item.name w))
               (mapcar
                  (lambda(syl)
                     (if(equal? 1 (item.feat syl 'stress))
                        (begin
                           (item.set_feat syl 'accented (item.feat token 'star_accent))
                           (mapcar
                              (lambda(seg)
                                 (item.set_feat seg 'star_accent 
                                                    (item.feat token 'star_accent)))
                              (item.daughters syl)))
                           (item.set_feat syl 'accented -1)))
                  (item.relation.daughters w 'SylStructure)))
            (item.daughters token))
         (mapcar
            (lambda(w)
               ;;(format t "\tword name is %l\n" (item.name w))
               (mapcar
                  (lambda(syl)
                     (if(equal? 1 (item.feat syl 'stress))
                        (item.set_feat syl 'accented 0)
                        (item.set_feat syl 'accented -1)))
                  (item.relation.daughters w 'SylStructure)))
            (item.daughters token)))
   
   
      (set! token (item.next token)))))




(provide 'star_accent)
