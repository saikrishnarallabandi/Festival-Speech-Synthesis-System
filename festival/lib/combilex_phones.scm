;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;                                                                       ;;
;;;                Centre for Speech Technology Research                  ;;
;;;                     University of Edinburgh, UK                       ;;
;;;                       Copyright (c) 2003, 2008                        ;;
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
;;; combilex phoneset
;;;


(defPhoneSet
  combilex
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
   (p      - 0 0 0 0 s l -) ;p 
   (t      - 0 0 0 0 s a -) ;t 
   (?      - 0 0 0 0 s g +) ;? 
   (t^      - 0 0 0 0 t a +) ;t^ (use unilex symbol, not "4", since ints not allowed in htk)
   (k      - 0 0 0 0 s v -) ;k 
   (m      - 0 0 0 0 n l +) ;m 
   (b      - 0 0 0 0 s l +) ;b 
   (d      - 0 0 0 0 s a +) ;d 
   (g      - 0 0 0 0 s v +) ;g 
   (x      - 0 0 0 0 f v -) ;x 
   (tS     - 0 0 0 0 a p -) ;ch 
   (dZ     - 0 0 0 0 a p +) ;jh 
   (s      - 0 0 0 0 f a -) ;s 
   (z      - 0 0 0 0 f a +) ;z 
   (S      - 0 0 0 0 f p -) ;sh 
   (Z      - 0 0 0 0 f p +) ;zh 
   (f      - 0 0 0 0 f b -) ;f 
   (v      - 0 0 0 0 f b +) ;v 
   (T      - 0 0 0 0 f d -) ;th 
   (D      - 0 0 0 0 f d +) ;dh 
   (h      - 0 0 0 0 f g -) ;h => changed to glottal fricative
   (m!     - 0 0 0 0 n l +) ;m!(use unilex symbol, not "m=", since doesn't work for hts) 
   (n      - 0 0 0 0 n a +) ;n 
   (n!     - 0 0 0 0 n a +) ;n!(use unilex symbol, not "m=", since doesn't work for htk) 
   (N      - 0 0 0 0 n v +) ;ng 
   (l      - 0 0 0 0 l a +) ;l => changed from approximant to liquid 
   (K      - 0 0 0 0 l a -) ;ll => .. + changed from voiced to voiceless
   (lw      - 0 0 0 0 l a +) ;lw => .. + (use unilex symbol, not "5", as ints bad for hts)
   (l!     - 0 0 0 0 l a +) ;l! => .. +(use unilex symbol, not "l=", as that's bad for hts)
   (r      - 0 0 0 0 r a +) ;r 
   (j      - 0 0 0 0 l p +) ;y 
   (w      - 0 0 0 0 l l +) ;w 
   (W      - 0 0 0 0 f l -) ;hw => changed from liquid to fricative, and to voiceless 
   (E      + s 2 1 - 0 0 0) ;e 
   (a      + s 3 1 - 0 0 0) ;a 
   (A      + l 3 3 - 0 0 0) ;aa => changed length and to back
   (Ar     + l 3 3 - 0 0 0) ;ar => ...
   (@U     + d 2 3 + 0 0 0) ;ou 
   (o~     + l 2 3 + n 0 0) 
   (e~     + l 2 1 + n 0 0) 
   (9~     + l 3 1 + n 0 0) 
   (Q      + s 3 3 + 0 0 0) ;o => changed length to short
   (QO     + l 3 3 + 0 0 0) ;au => not clear this is a surface symbol!
   (O      + l 2 3 + 0 0 0) ;oo => changed height to mid 
   (Or     + l 2 3 + 0 0 0) ;or => changed height to mid
   (@Ur    + l 2 3 + 0 0 0) ;our 
   (i      + l 1 1 - 0 0 0) ;ii 
   (iy     + s 1 1 - 0 0 0) ;iy 
   (I      + s 1 1 - 0 0 0) ;i 
   (@r     + a 2 2 - 0 0 0) ;@r <= changed from having consonant features (e.g. approximant) 
   (@      + a 2 2 - 0 0 0) ;@ 
   (V      + s 3 2 - 0 0 0) ;uh <= changed from mid to low (e.g. STRUT)
   (U      + s 1 3 + 0 0 0) ;u  <= change from long to short (e.g. FOOT)
   (u      + l 1 3 + 0 0 0) ;uu 
   (eI     + d 2 1 - 0 0 0) ;ei 
   (aI     + d 3 2 - 0 0 0) ;ai 
   (aIr    + d 3 2 - 0 0 0) ;ai 
   (ae     + d 3 2 - 0 0 0) ;ae 
   (aer    + d 3 2 - 0 0 0) ;aer 
   (OI     + d 2 3 + 0 0 0) ;oi 
   (OIr    + d 2 3 + 0 0 0) ;oir 
   (aU     + d 3 2 - 0 0 0) ;ow 
   (aUr    + d 3 2 - 0 0 0) ;owr 
   (i@     + d 1 1 - 0 0 0) ;i@ <= changed to diphthong 
   (I@     + d 1 1 - 0 0 0) ;ir <= changed to diphthong
   (@@      + l 2 2 - 0 0 0) ; <= changed to long vowel (and not using "3", since that's bad for hts)
   (@@r     + l 2 2 - 0 0 0) ; <= added in, e.g. Nurse <= changed to long vowel (and not using "3r", since that's bad for hts)
   (Er     + s 2 1 - 0 0 0) ;er 
   (E@     + d 2 1 - 0 0 0) ;eir 
   (U@     + d 1 3 + 0 0 0) ;ur <= changed to diphthong
  )
)

(PhoneSet.silences '( # SIL))

(define (combilex::select_phoneset)
  "(combilex::select_phoneset)
Set up phone set for combilex"
  (Parameter.set 'PhoneSet 'combilex)
  (PhoneSet.select 'combilex)
)

(define (combilex::reset_phoneset)
  "(combilex::reset_phoneset)
Reset phone set for combilex."
  t
)

(provide 'combilex_phones)
