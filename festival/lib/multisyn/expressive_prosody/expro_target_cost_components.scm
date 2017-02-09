
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
;;;  Utility functions and target cost components for expro_target_cost.scm, 
;;;  re-implemented in Scheme by looking at EST_TargetCost.cc.
;;;  There is a similar implementation in ../target_cost.scm of which I was
;;;  not aware.

(require 'expro_util)


(define (ph_is_vowel seg)
"
(ph_is_vowel segment_item)
"
(if seg
   (equal? "+" (item.feat seg 'ph_vc))
   nil))

(define (ph_is_nasal_liquid_or_approximant  seg)
"
(ph_is_nasal_liquid_or_approximant  segment_item)

consonant type: stop fricative affricate nasal lateral approximant
ctype           s    f         a         n     l       r
Liquids are /l/ and /r/, with /l/ being the only lateral 
and /r/ being an approximant.
"
(if seg
   (string-matches (item.feat seg 'ph_ctype) "[nlr]")
   nil))


; from EST_TargetCost.cc
(define (simple_pos pos)
"
(simple_pos pos)

Replica of EST_TargetCost::simple_pos()
simplifies e.g.  nn|nnp|nns|nnps|fw|sym|ls -> n
"
(cond
   ((string-matches pos "\\(nn.*\\)\\|\\(fw\\)\\|\\(ls\\)\\|\\(sym\\)")
      "n")
   ((string-matches pos "vb.*")
      "vb")
   ((string-matches pos "\\(jj.*\\)\\|\\(rb.*\\)\\|\\(rp\\)")
      "other")
   (t
      "func")))
   
  
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define (expro_stress_cost targ_seg cand_seg)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
"(expro_stress_cost targ_seg cand_seg)

Replica of EST_TargetCost::stress_cost();  Returns 0 or 1.
"
;; left-hand side of the diphone
(if(ph_is_vowel targ_seg)
   (begin
      (set! targ_syl (item.relation.Parent targ_seg 'SylStructure))
      (set! cand_syl (item.relation.Parent cand_seg 'SylStructure))
      (if cand_syl ;; Can't assume candidate is a vowel, too, and belongs to 
         (begin    ;; a syllable (because of backoff to a silence for example)
            (set! targ_stress (if(equal? 0 (item.feat targ_syl 'stress)) 0 1))
            (set! cand_stress (if(equal? 0 (item.feat cand_syl 'stress)) 0 1))
            (if(equal? targ_stress cand_stress)
               (set! left_stress_disagree nil)
               (set! left_stress_disagree t)))
          (set! left_stress_disagree t)))
   (set! left_stress_disagree nil))
;; right-hand side of diphone:
(if(ph_is_vowel(item.next targ_seg))
   (begin
      (set! targ_syl (item.relation.Parent (item.next targ_seg) 'SylStructure))
      (set! cand_syl (item.relation.Parent (item.next cand_seg) 'SylStructure))
      (if cand_syl ;; Can't assume candidate is a vowel, too, and this belongs
         (begin    ;; to a syllable (because of backoff to a silence for example)
            (set! targ_stress (if(equal? 0 (item.feat targ_syl 'stress)) 0 1))
            (set! cand_stress (if(equal? 0 (item.feat cand_syl 'stress)) 0 1))
            (if(equal? targ_stress cand_stress)
               (set! right_stress_disagree nil)
               (set! right_stress_disagree t)))
         (set! right_stress_disagree t)))
   (set! right_stress_disagree nil))
(if(or left_stress_disagree right_stress_disagree)
   1
   0))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define (expro_position_in_syllable_cost targ_seg cand_seg)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
"(expro_position_in_syllable_cost targ_seg cand_seg)

Replica of EST_TargetCost::position_in_syllable_cost():
Distinguishes positions  INTER   (i.e. bridges a syllable boundary)
                         FINAL   (right half of diphone is syl-final phone)
                         INITIAL (includes SINGLE i.e. INITIAL && FINAL)
                         MEDIAL
returns 0 if positions are equal, 1 else.
"
(set! targ_syl           (item.relation.Parent                      targ_seg 'SylStructure))
(set! targ_prev_syl      (item.relation.Parent           (item.prev targ_seg) 'SylStructure))
(set! targ_next_syl      (item.relation.Parent           (item.next targ_seg) 'SylStructure))
(set! targ_next_next_syl (item.relation.Parent (item.next(item.next targ_seg)) 'SylStructure))
(if(not(equal? targ_syl targ_next_syl))
   (set! targ_pos 'TCPOS_INTER)
   (if(not(equal? targ_syl targ_prev_syl))
      (set! targ_pos 'TCPOS_INITIAL)
      (if(not(equal? targ_next_syl targ_next_next_syl))
         (set! targ_pos 'TCPOS_FINAL)
         (set! targ_pos 'TCPOS_MEDIAL))))
;;(format t "position_in_syllable: targ_pos %l\n" targ_pos)

(set! cand_syl           (item.relation.Parent                      cand_seg 'SylStructure))
(set! cand_prev_syl      (item.relation.Parent           (item.prev cand_seg) 'SylStructure))
(set! cand_next_syl      (item.relation.Parent           (item.next cand_seg) 'SylStructure))
(set! cand_next_next_syl (item.relation.Parent (item.next(item.next cand_seg)) 'SylStructure))
(if(not(equal? cand_syl cand_next_syl))
   (set! cand_pos 'TCPOS_INTER)
   (if(not(equal? cand_syl cand_prev_syl))
      (set! cand_pos 'TCPOS_INITIAL)
      (if(not(equal? cand_next_syl cand_next_next_syl))
         (set! cand_pos 'TCPOS_FINAL)
         (set! cand_pos 'TCPOS_MEDIAL))))
;;(format t "position_in_syllable: cand_pos %l\n" cand_pos)

(if(equal? targ_pos cand_pos)
   0
   1))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define (expro_position_in_word_cost targ_seg cand_seg)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
"(expro_position_in_word_cost targ_seg cand_seg)

Replica of EST_TargetCost::position_in_word_cost():
Distinguishes positions  INTER   (i.e. bridges a word boundary)
                         FINAL   (right half of diphone is word-final phone)
                         INITIAL (includes SINGLE i.e. INITIAL && FINAL)
                         MEDIAL
returns 0 if positions are equal, 1 else.

"

(set! targ_wrd           (item.root(item.relation.Parent                      targ_seg 'SylStructure)))
(set! targ_prev_wrd      (item.root(item.relation.Parent           (item.prev targ_seg) 'SylStructure)))
(set! targ_next_wrd      (item.root(item.relation.Parent           (item.next targ_seg) 'SylStructure)))
(set! targ_next_next_wrd (item.root(item.relation.Parent (item.next(item.next targ_seg)) 'SylStructure)))
(if(not(equal? targ_wrd targ_next_wrd))
   (set! targ_pos 'TCPOS_INTER)
   (if(not(equal? targ_wrd targ_prev_wrd))
      (set! targ_pos 'TCPOS_INITIAL)
      (if(not(equal? targ_next_wrd targ_next_next_wrd))
         (set! targ_pos 'TCPOS_FINAL)
         (set! targ_pos 'TCPOS_MEDIAL))))
;;(format t "position_in_word: targ_pos %l\n" targ_pos)

(set! cand_wrd           (item.root(item.relation.Parent                      cand_seg 'SylStructure)))
(set! cand_prev_wrd      (item.root(item.relation.Parent           (item.prev cand_seg) 'SylStructure)))
(set! cand_next_wrd      (item.root(item.relation.Parent           (item.next cand_seg) 'SylStructure)))
(set! cand_next_next_wrd (item.root(item.relation.Parent (item.next(item.next cand_seg)) 'SylStructure)))
(if(not(equal? cand_wrd cand_next_wrd))
   (set! cand_pos 'TCPOS_INTER)
   (if(not(equal? cand_wrd cand_prev_wrd))
      (set! cand_pos 'TCPOS_INITIAL)
      (if(not(equal? cand_next_wrd cand_next_next_wrd))
         (set! cand_pos 'TCPOS_FINAL)
         (set! cand_pos 'TCPOS_MEDIAL))))
;;(format t "position_in_word: cand_pos %l\n" cand_pos)


(if(equal? targ_pos cand_pos)
   0
   1))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define (expro_partofspeech_cost targ_seg cand_seg)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
"(expro_partofspeech_cost targ_seg cand_seg)
Replica of EST_TargetCost:partofspeech_cost:
Returns 0 if the simplified POS(targ) and POS(cand) agree for both 
half phones, 1 else.  If both POS(targ) and POS(cand) are undefined,
this counts as agreement, too.
"


(set! targ_wrd(item.root(item.relation.Parent targ_seg 'SylStructure)))
(set! cand_wrd(item.root(item.relation.Parent cand_seg 'SylStructure)))
(if targ_wrd
   (if cand_wrd
      (begin
         (set! targ_pos (simple_pos (item.feat targ_wrd 'pos)))
         (set! cand_pos (simple_pos (item.feat cand_wrd 'pos)))
         (if(string-equal targ_pos cand_pos)
            ;;;;;;;;;;;;;;; agreement of left-hand side POS   ;;;;;;;;;;;;
            ;;;;;;;;;          now check right-hand side         ;;;;;;;;;
            (begin

               (set! targ_wrd(item.root(item.relation.Parent(item.next targ_seg) 'SylStructure)))
               (set! cand_wrd(item.root(item.relation.Parent(item.next cand_seg) 'SylStructure)))
               (if targ_wrd
                  (if cand_wrd
                     (begin
                        (set! targ_pos (simple_pos (item.feat targ_wrd 'pos)))
                        (set! cand_pos (simple_pos (item.feat cand_wrd 'pos)))
                        (if(string-equal targ_pos cand_pos)
                           0
                           1))
                     1)
                  (if cand_wrd
                     1
                     0)))
            ;;;;;;;;;      End of checking right-hand side       ;;;;;;;;;

            1))
      1)
   (if cand_wrd
      1
      0)))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define (expro_position_in_phrase_cost targ_seg cand_seg)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
"(expro_position_in_phrase_cost targ_seg cand_seg)
Replica of EST_TargetCost::position_in_phrase_cost:
Returns 0 if word feature pbreak is the same, 0 else."

(set! targ_syl (item.relation.Parent targ_seg 'SylStructure))
(set! cand_syl (item.relation.Parent cand_seg 'SylStructure))
(if targ_syl
   (if cand_syl
      (begin
         (set! targ_pbreak (item.feat (item.Parent targ_syl) 'pbreak))
         (set! cand_pbreak (item.feat (item.Parent cand_syl) 'pbreak))
         (if(string-equal targ_pbreak cand_pbreak)
            0
            1))
      1)
   (if cand_syl
      1
      0)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define (expro_left_context_cost targ_seg cand_seg)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
"(expro_left_context_cost targ_seg cand_seg)
Replica of  EST_TargetCost::left_context_cost() 
except that it looks out for feature 'left_context:
Returns 0 if equal, 1 else.
"
(set! targ_seg (item.relation targ_seg 'Segment))
(set! cand_seg (item.relation cand_seg 'Segment))
(if(not(equal? 0 (item.feat targ_seg 'left_context)))
   (set! prev_targ_seg_name (item.feat targ_seg 'left_context))
   (begin
      (set! prev_targ_seg (item.prev targ_seg))
      (if prev_targ_seg
         (set! prev_targ_seg_name (item.name prev_targ_seg))
         (set! prev_targ_seg_name "0"))))
(if(not(equal? 0 (item.feat cand_seg 'left_context)))
   (set! prev_cand_seg_name (item.feat cand_seg 'left_context))
   (begin
      (set! prev_cand_seg (item.prev cand_seg))
      (if prev_cand_seg
         (set! prev_cand_seg_name (item.name prev_cand_seg))
         (set! prev_cand_seg_name "0"))))
(if(string-equal prev_targ_seg_name prev_cand_seg_name)
   0
   1))
   
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define (expro_right_context_cost targ_seg cand_seg)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
"(expro_right_context_cost targ_seg cand_seg)
Replica of  EST_TargetCost::right_context_cost():
except that it looks out for feature 'right_context:
Returns 0 if equal, 1 else."
(set! next_targ_seg (item.relation.next targ_seg 'Segment));right hand side of diph
(set! next_cand_seg (item.relation.next cand_seg 'Segment))
(if(not(equal? 0 (item.feat next_targ_seg 'right_context)))
   (set! next_next_targ_seg_name (item.feat next_targ_seg 'right_context))
   (begin
      (set! next_next_targ_seg (item.next next_targ_seg))
      (if next_next_targ_seg
         (set! next_next_targ_seg_name(item.name next_next_targ_seg))
         (set! next_next_targ_seg_name "0"))))
(if(not(equal? 0 (item.feat next_cand_seg 'right_context)))
   (set! next_next_cand_seg_name (item.feat next_cand_seg 'right_context))
   (begin
      (set! next_next_cand_seg (item.next next_cand_seg))
      (if next_next_cand_seg
         (set! next_next_cand_seg_name(item.name next_next_cand_seg))
         (set! next_next_cand_seg_name "0"))))
(if(string-equal next_next_targ_seg_name next_next_cand_seg_name)
   0
   1))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define (expro_inner_context_cost targ_seg cand_seg)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
"(expro_inner_context_cost targ_seg cand_seg)

Inner context refers to a deleted stop because it was immediately 
followed by another stop (see (postlex_stop_deletion utt)). 

Consider:

backtrack /b a k t r a k/ -> /b a t r a k/
If we then look for a diphone /a t/ we want to favour
candidates coming from the same context i.e. which 
are actually a reduced /a k t/.  In the data base, 
the 1st /a/ gets the feature right_context=k and the 
/t/ gets the fearture left_context=k.
"
(if(equal? 0 (item.feat targ_seg 'right_context))
   0
   (begin
      (set! inner_context (item.feat targ_seg 'right_context))
      (set! rico_cand_seg (item.feat cand_seg 'right_context))
      (set! leco_cand_seg (item.feat (item.next cand_seg) 'left_context))
      (if(and(equal? inner_context rico_cand_seg)
             (equal? inner_context leco_cand_seg))
         0
         1))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(set! debug_bad_duration_cost t)

(define (expro_bad_duration_cost targ_seg cand_seg)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
"(expro_bad_duration_cost targ_seg cand_seg)
Returns 1 if either left or right hand side of cand_seg 
has 'bad_dur flag, else 0.
"
(set! cand_left cand_seg)
(set! cand_right (item.next cand_left))
(set! reval 0)
(if(not(equal? 0 (item.feat cand_left 'bad_dur)))
   (set! reval 1))
(if(not(equal? 0 (item.feat cand_right 'bad_dur)))
   (set! reval 1))
reval)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define (expro_bad_f0_cost targ_seg cand_seg)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
"(expro_bad_f0_cost targ_seg cand_seg)

Requires segment feature mid_f0, with unvoiced encoded as -1.

Returns 1 if either left or right hand side of candidate is
* voiced but not a stop or fricative AND
* mid_f0 is -1

and 0 else.

"
(set! cand_left cand_seg)
(set! cand_right (item.next cand_left))

(if(or(ph_is_vowel cand_left)(ph_is_nasal_liquid_or_approximant cand_left))
   (if (equal? -1 (item.feat cand_left 'mid_f0))
      1
      (if(or(ph_is_vowel cand_right)(ph_is_nasal_liquid_or_approximant cand_right))
         (if (equal? -1 (item.feat cand_right 'mid_f0))
            1
            0)
         0))
   0))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define (expro_emph_cost targ_seg cand_seg)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
"(expro_emph_cost targ_seg cand_seg)

"
(if(ph_is_vowel targ_seg)
   (if(equal?(item.feat targ_seg 'emph)
             (item.feat cand_seg 'emph))
      (set! left_emph_disagree nil)
      (set! left_emph_disagree t))
   (set! left_emph_disagree nil))

(if(ph_is_vowel (item.next targ_seg))
   (if(equal?(item.feat (item.next targ_seg) 'emph)
             (item.feat (item.next cand_seg) 'emph))
      (set! right_emph_disagree nil)
      (set! right_emph_disagree t))
   (set! right_emph_disagree nil))
(if(or left_emph_disagree right_emph_disagree)
   1
   0))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define (expro_btone_cost targ_seg cand_seg)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
"(expro_btone_cost targ_seg cand_seg)

"
(if(ph_is_vowel targ_seg)
   (if(equal?(item.feat targ_seg 'btone)
             (item.feat cand_seg 'btone))
      (set! left_btone_disagree nil)
      (set! left_btone_disagree t))
   (set! left_btone_disagree nil))

(if(ph_is_vowel (item.next targ_seg))
   (if(equal?(item.feat (item.next targ_seg) 'btone)
             (item.feat (item.next cand_seg) 'btone))
      (set! right_btone_disagree nil)
      (set! right_btone_disagree t))
   (set! right_btone_disagree nil))
(if(or left_btone_disagree right_btone_disagree)
   1
   0))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define (expro_star_accent_cost targ_seg cand_seg)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
"(expro_star_accent_cost targ_seg cand_seg)

Returns 1 if either half of the diphone is a vowel and 
the feature 'star_accent of targ_seg cand_seg do not agree;
0 else.

This is for the 2-way classifier i.e. 'star_accent should be 
either 1 or 0.
"
(set! reval 0)
(if(ph_is_vowel targ_seg)
   (if(not(equal? (item.feat targ_seg 'star_accent)
                  (item.feat cand_seg 'star_accent)))
      (set! reval 1)))
(if(ph_is_vowel (item.next targ_seg))
   (if(not(equal? (item.feat (item.next targ_seg) 'star_accent)
                  (item.feat (item.next cand_seg) 'star_accent)))
      (set! reval 1)))
reval)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define (expro_STAR_accent_cost targ_seg cand_seg)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
"(expro_STAR_accent_cost targ_seg cand_seg)

This is for the 3-way classifier which gives the segment 
feature 'star_accent the value
-1 for de-accented
 0 for optionally accented
 1 for accented.

Returns 1 if either half of the diphone is a vowel and 
the feature 'star_accent of targ_seg and cand_seg do not 
agree WHEN TARG_SEG IS NOT 0 (i.e. when accentuation is 
not optional); 0 else:

targ_seg  cand_seg  return
    -1        -1       0
    -1         0       1
    -1         1       1
     0        -1       0
     0         0       0
     0         1       0
     1        -1       1
     1         0       1
     1         1       0
"
(set! reval 0)
(if(ph_is_vowel targ_seg)
   (if(and(not(equal? 0 (item.feat targ_seg 'star_accent)))
          (not(equal? (item.feat targ_seg 'star_accent)
                      (item.feat cand_seg 'star_accent))))
      (set! reval 1)))
(if(ph_is_vowel (item.next targ_seg))
   (if(and(not(equal? 0 (item.feat (item.next targ_seg) 'star_accent)))
          (not(equal? (item.feat (item.next targ_seg) 'star_accent)
                      (item.feat (item.next cand_seg) 'star_accent))))
      (set! reval 1)))
reval)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define (expro_blacklisted_cost targ_seg cand_seg)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
"(expro_blacklisted_cost targ_seg cand_seg)

If symbol blacklist is bound to a list of bad units, 
specified by utterance name and end time each, e.g.
'((\"roger_3163\" 0.542) (\"roger_3276\" 2.266))
then these units are penalized by the target cost.  

Get utterance names and ent times from (dump_costs utt).

End times need not be exact, tolerance is +-100ms. End 
time 0 will discard the entire untterance.  


This requires that the segment have the feature 'uid
(utterance ID).  See (add_feature_uid utt) and function 
apply_to_utts. 

"
(set! reval 0)
(let (bad_utt uid cand_end_time)
   (if(symbol-bound? 'blacklist)
      (begin
          ;;; (set! uid (utt.feat (item.get_utt cand_seg 'fileid)))
          ;;; does not work since item.get_utt does not work here.
          (set! uid (item.feat cand_seg 'uid))
          (set! bad_utt (assoc_string uid blacklist))
          (if bad_utt
             (begin
                (set! end_time (car(cdr bad_utt)))
                (set! cand_end_time (item.feat cand_seg 'end))
                (if(or(< (fabs(- end_time cand_end_time)) 0.1)
                      (eqv? end_time 0))
                   (begin
                      (format t "%s end time %f blacklisted\n" (car bad_utt) 
                                                   (item.feat cand_seg 'end))
                      (set! reval 1))))))))

reval)

; (set! blacklist '( ("roger_3163" 0.542) ("roger_3946" 3.0320001)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define (add_feature_uid utt)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
"(add_feature_uid utt)

copy the utterance ID (utt.feat utt 'fileid) to each
segment as feature 'uid.

To do that for all utterances,
(load \"all.stp\") (apply_to_utts add_feature_uid all)

"
(mapcar
    (lambda(seg)
       (item.set_feat seg 'uid (utt.feat utt 'fileid)))
    (utt.relation.items utt 'Segment)))


(provide 'expro_target_cost_star)
