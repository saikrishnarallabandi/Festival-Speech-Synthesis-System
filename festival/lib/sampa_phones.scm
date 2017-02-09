;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;                                                                       ;;
;;;                Centre for Speech Technology Research                  ;;
;;;                     University of Edinburgh, UK                       ;;
;;;                         Copyright (c) 2007                            ;;
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
;;; SAMPA phoneset for German                       Volker Strom, 30/05/2007
;;;


(defPhoneSet
  sampa
  ;;;  Phone Features
  (;; vowel or consonant
   (vc + -)  
   ;; vowel length: short long dipthong schwa
   (vlng s l d a 0)
   ;; vowel height: high mid low
   (vheight 1 2 3 0)
   ;; vowel frontness: front mid back
   (vfront 1 2 3 0)
   ;; lip rounding
   (vrnd + - 0)
   ;; consonant type: stop fricative affricative nasal liquid approximant
   (ctype s f a n l t r 0)
   ;; place of articulation: labial alveolar palatal labio-dental
   ;;                         dental velar glottal
   (cplace l a p b d v g 0)
   ;; consonant voicing
   (cvox + - 0)
   )
  (
   (SIL  - 0 0 0 0 0 0 -)  ;; slience ... 
   (sil  - 0 0 0 0 0 0 -)  ;; slience ... 
   (sp   - 0 0 0 0 0 0 -)  ;; slience ... 
   (#  - 0 0 0 0 0 0 -)  ;; slience ... 
   (B_10  - 0 0 0 0 0 0 -)  ;; Pauses
   (B_20 - 0 0 0 0 0 0 -)  ;; Pauses
   (B_30 - 0 0 0 0 0 0 -)  ;; Pauses
   (B_40 - 0 0 0 0 0 0 -)  ;; Pauses
   (B_50 - 0 0 0 0 0 0 -)  ;; Pauses
   (B_100 - 0 0 0 0 0 0 -)  ;; Pauses
   (B_150 - 0 0 0 0 0 0 -)  ;; Pauses
   (B_200 - 0 0 0 0 0 0 -)  ;; Pauses
   (B_250 - 0 0 0 0 0 0 -)  ;; Pauses
   (B_300 - 0 0 0 0 0 0 -)  ;; Pauses
   (B_400 - 0 0 0 0 0 0 -)  ;; Pauses
   (IGNORE - 0 0 0 0 0 0 -)  ;; Pauses


   ;; insert the phones here, see examples in 
   ;; festival/lib/*_phones.scm

   ;(name vc vling vheight vfront vrnd ctype cplace cvox)

   ;;; Volker guesed these values.
   ;;; Not to be taken too seriously.

   (p    -   0   0   0   0   s   l   -)
   (t    -   0   0   0   0   s   a   -)
   (?    -   0   0   0   0   s   g   +) 
   (GS   -   0   0   0   0   s   g   +) 
   (k    -   0   0   0   0   s   v   -)
   (x    -   0   0   0   0   f   v   -)
   (b    -   0   0   0   0   s   l   +)
   (d    -   0   0   0   0   s   a   +)
   (g    -   0   0   0   0   s   v   +)
   (tS   -   0   0   0   0   a   p   -)
   (ts   -   0   0   0   0   a   a   -)
   (tZ   -   0   0   0   0   a   p   +)
   (pf   -   0   0   0   0   a   b   +)
   (s    -   0   0   0   0   f   a   -)
   (z    -   0   0   0   0   f   a   +)
   (S    -   0   0   0   0   f   p   -)
   (Z    -   0   0   0   0   f   p   +)
   (f    -   0   0   0   0   f   b   -)
   (v    -   0   0   0   0   f   b   +)
   (h    -   0   0   0   0   f   0   -) 
   (m    -   0   0   0   0   n   l   +)
   (n    -   0   0   0   0   n   a   +)
   (N    -   0   0   0   0   n   v   +)
   (l    -   0   0   0   0   r   a   +)
   (r    -   0   0   0   0   r   a   +)
   (j    -   0   0   0   0   l   p   +)
   (w    -   0   0   0   0   l   l   +)
   (e:   +   l   2   1   -   0   0   0)
   (E:   +   l   2   1   -   0   0   0)
   (E~:  +   l   2   1   -   0   0   0)
   (E    +   s   2   1   -   0   0   0)
   (E~   +   s   2   1   -   0   0   0)
   (a:   +   l   3   1   -   0   0   0)
   (a    +   s   3   1   -   0   0   0)
   (A    +   s   2   2   -   0   0   0) 
   (A:   +   l   2   2   -   0   0   0) 
   (A~:  +   l   2   2   -   0   0   0) 
   (aU   +   d   3   2   -   0   0   0)
   (o:   +   l   3   3   +   0   0   0)
   (O:   +   l   3   3   -   0   0   0)
   (O~:  +   l   3   3   -   0   0   0)
   (O    +   s   3   3   -   0   0   0)
   (2:   +   l   3   1   +   0   0   0)
   (3:   +   l   3   1   +   0   0   0)
   (9~:  +   l   3   1   -   0   0   0)
   (9.   +   s   3   1   -   0   0   0)
   (i:   +   l   1   1   -   0   0   0)
   (I    +   s   1   1   -   0   0   0)
   (@r   +   a   2   2   -   0   0   0)
   (@    +   a   2   2   -   0   0   0)
   (u:   +   l   2   3   +   0   0   0)
   (U    +   s   2   3   +   0   0   0)
   (Y:   +   l   2   1   +   0   0   0)
   (Y    +   s   2   1   +   0   0   0)
   (eI   +   d   2   1   -   0   0   0)
   (aI   +   d   3   2   -   0   0   0)    
   (OY   +   d   2   3   +   0   0   0)    
  )
)

(PhoneSet.silences '( # SIL))

(define (sampa::select_phoneset)
  "(sampa::select_phoneset)
Set up phone set for sampa"
  (Parameter.set 'PhoneSet 'sampa)
  (PhoneSet.select 'sampa)
)

(define (sampa::reset_phoneset)
  "(sampa::reset_phoneset)
Reset phone set for sampa."
  t
)

(provide 'sampa_phones)
