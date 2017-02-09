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
;;;  Target cost functions re-implemented in Scheme by looking at 
;;;  EST_TargetCost.cc (revision 1.11 and earlier; the weights changed 
;;   in revision 1.12 of May 2006).
;;;  There is a similar implementation in ../target_cost.scm of which I was
;;;  not aware of.
;;;
;;; 12/02/2007  expro_inner_context_cost added which deals with deleted stops.
;;; 19/06/2007  expro_target_cost_default added
;;; 11/04/2008  expro_target_cost_slim[12] added

(require 'expro_target_cost_components)

(set! gtcw 10) ; Global Target Cost Weight i.e. importance over join cost

(define (expro_target_cost targ_seg cand_seg)
"
(expro_target_cost targ_seg cand_seg)
The defaut target cost components, plus
32 * expro_emph_cost
32 * expro_btone_cost

Usage: (du_voice.setTargetCost VOICE expro_target_cost)
"
(set! cost 0)
(set! cost (+ cost (* 10 (expro_stress_cost               targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_position_in_syllable_cost targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_position_in_word_cost     targ_seg cand_seg))))
(set! cost (+ cost (*  6 (expro_partofspeech_cost         targ_seg cand_seg))))
(set! cost (+ cost (*  7 (expro_position_in_phrase_cost   targ_seg cand_seg))))
(set! cost (+ cost (*  4 (expro_left_context_cost         targ_seg cand_seg))))
(set! cost (+ cost (*  3 (expro_right_context_cost        targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_inner_context_cost        targ_seg cand_seg))))
(set! cost (+ cost (* 10 (expro_bad_duration_cost         targ_seg cand_seg))))
(set! cost (+ cost (* 25 (expro_bad_f0_cost               targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_emph_cost                 targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_btone_cost                targ_seg cand_seg))))
;(set! cost (+ cost (* 32 (expro_star_accent_cost          targ_seg cand_seg))))
(set! cost (+ cost (* 999 (expro_blacklisted_cost         targ_seg cand_seg))))
(set! cost (* gtcw (/ cost (+ 10 5 5 6 7 4 3 5 10 25 32 32))))

cost)

(define (expro_target_cost_pos_boosted targ_seg cand_seg)
"
(expro_target_cost_pos_boosted targ_seg cand_seg)
Like expro_target_cost but the weight of expro_partofspeech_cost
is boosted from 6 to 38.  This is for comparison with 
expro_target_cost_star, which is like expro_target_cost 
but with an extra expro_star_accent_cost component whose 
weight is 32.


Usage: (du_voice.setTargetCost VOICE expro_target_cost_pos_boosted)
"
(set! cost 0)
(set! cost (+ cost (* 10 (expro_stress_cost               targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_position_in_syllable_cost targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_position_in_word_cost     targ_seg cand_seg))))
(set! cost (+ cost (* 38 (expro_partofspeech_cost         targ_seg cand_seg))))
(set! cost (+ cost (*  7 (expro_position_in_phrase_cost   targ_seg cand_seg))))
(set! cost (+ cost (*  4 (expro_left_context_cost         targ_seg cand_seg))))
(set! cost (+ cost (*  3 (expro_right_context_cost        targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_inner_context_cost        targ_seg cand_seg))))
(set! cost (+ cost (* 10 (expro_bad_duration_cost         targ_seg cand_seg))))
(set! cost (+ cost (* 25 (expro_bad_f0_cost               targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_emph_cost                 targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_btone_cost                targ_seg cand_seg))))
;(set! cost (+ cost (* 32 (expro_star_accent_cost          targ_seg cand_seg))))
(set! cost (+ cost (* 999 (expro_blacklisted_cost         targ_seg cand_seg))))
(set! cost (* gtcw (/ cost (+ 10 5 5 38 7 4 3 5 10 25 32 32))))

cost)

(define (expro_target_cost_default targ_seg cand_seg)
"
(expro_target_cost_default targ_seg cand_seg)
The defaut target cost components (prior revision 1.12).

Probably requires a lower global target cost weight than 10.
Try (set! gtcw 7)

Usage: (du_voice.setTargetCost VOICE expro_target_cost_default)
"
(set! cost 0)
(set! cost (+ cost (* 10 (expro_stress_cost               targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_position_in_syllable_cost targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_position_in_word_cost     targ_seg cand_seg))))
(set! cost (+ cost (*  6 (expro_partofspeech_cost         targ_seg cand_seg))))
(set! cost (+ cost (*  7 (expro_position_in_phrase_cost   targ_seg cand_seg))))
(set! cost (+ cost (*  4 (expro_left_context_cost         targ_seg cand_seg))))
(set! cost (+ cost (*  3 (expro_right_context_cost        targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_inner_context_cost        targ_seg cand_seg))))
(set! cost (+ cost (* 10 (expro_bad_duration_cost         targ_seg cand_seg))))
(set! cost (+ cost (* 25 (expro_bad_f0_cost               targ_seg cand_seg))))
;(set! cost (+ cost (* 32 (expro_emph_cost                 targ_seg cand_seg))))
;(set! cost (+ cost (* 32 (expro_btone_cost                targ_seg cand_seg))))
;(set! cost (+ cost (* 32 (expro_star_accent_cost          targ_seg cand_seg))))
(set! cost (+ cost (* 999 (expro_blacklisted_cost         targ_seg cand_seg))))
(set! cost (* gtcw (/ cost (+ 10 5 5 6 7 4 3 5 10 25))))

cost)

(define (expro_target_cost_star targ_seg cand_seg)
"
(expro_target_cost_star targ_seg cand_seg)
The defaut target cost components, plus
32 * expro_emph_cost
32 * expro_btone_cost
32 * expro_star_accent_cost  (for the 2-way classifier +-accent)

Usage: (du_voice.setTargetCost VOICE expro_target_cost_star)
"
(set! cost 0)
(set! cost (+ cost (* 10 (expro_stress_cost               targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_position_in_syllable_cost targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_position_in_word_cost     targ_seg cand_seg))))
(set! cost (+ cost (*  6 (expro_partofspeech_cost         targ_seg cand_seg))))
(set! cost (+ cost (*  7 (expro_position_in_phrase_cost   targ_seg cand_seg))))
(set! cost (+ cost (*  4 (expro_left_context_cost         targ_seg cand_seg))))
(set! cost (+ cost (*  3 (expro_right_context_cost        targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_inner_context_cost        targ_seg cand_seg))))
(set! cost (+ cost (* 10 (expro_bad_duration_cost         targ_seg cand_seg))))
(set! cost (+ cost (* 25 (expro_bad_f0_cost               targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_emph_cost                 targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_btone_cost                targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_star_accent_cost          targ_seg cand_seg))))
(set! cost (+ cost (* 999 (expro_blacklisted_cost         targ_seg cand_seg))))
(set! cost (* gtcw (/ cost (+ 10 5 5 6 7 4 3 5 10 25 32 32 32))))

cost)


(define (expro_target_cost_STAR targ_seg cand_seg)
"
(expro_target_cost_STAR targ_seg cand_seg)
The defaut target cost components, plus
32 * expro_emph_cost
32 * expro_btone_cost
32 * expro_STAR_accent_cost (for the 3-way classifier: accented,
                             de-accented, optionally-accented)

Usage: (du_voice.setTargetCost VOICE expro_target_cost_STAR)
"
(set! cost 0)
(set! cost (+ cost (* 10 (expro_stress_cost               targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_position_in_syllable_cost targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_position_in_word_cost     targ_seg cand_seg))))
(set! cost (+ cost (*  6 (expro_partofspeech_cost         targ_seg cand_seg))))
(set! cost (+ cost (*  7 (expro_position_in_phrase_cost   targ_seg cand_seg))))
(set! cost (+ cost (*  4 (expro_left_context_cost         targ_seg cand_seg))))
(set! cost (+ cost (*  3 (expro_right_context_cost        targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_inner_context_cost        targ_seg cand_seg))))
(set! cost (+ cost (* 10 (expro_bad_duration_cost         targ_seg cand_seg))))
(set! cost (+ cost (* 25 (expro_bad_f0_cost               targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_emph_cost                 targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_btone_cost                targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_STAR_accent_cost          targ_seg cand_seg))))
(set! cost (+ cost (* 999 (expro_blacklisted_cost         targ_seg cand_seg))))
(set! cost (* gtcw (/ cost (+ 10 5 5 6 7 4 3 5 10 25 32 32 32))))

cost)


(define (expro_target_cost_STAR_noemph targ_seg cand_seg)
"
(expro_target_cost_STAR_noemph targ_seg cand_seg)
The defaut target cost components, plus
32 * expro_btone_cost
32 * expro_STAR_accent_cost (for the 3-way classifier: accented,
                             de-accented, optionally-accented)

Usage: (du_voice.setTargetCost VOICE expro_target_cost_STAR_noemph)
"
(set! cost 0)
(set! cost (+ cost (* 10 (expro_stress_cost               targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_position_in_syllable_cost targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_position_in_word_cost     targ_seg cand_seg))))
(set! cost (+ cost (*  6 (expro_partofspeech_cost         targ_seg cand_seg))))
(set! cost (+ cost (*  7 (expro_position_in_phrase_cost   targ_seg cand_seg))))
(set! cost (+ cost (*  4 (expro_left_context_cost         targ_seg cand_seg))))
(set! cost (+ cost (*  3 (expro_right_context_cost        targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_inner_context_cost        targ_seg cand_seg))))
(set! cost (+ cost (* 10 (expro_bad_duration_cost         targ_seg cand_seg))))
(set! cost (+ cost (* 25 (expro_bad_f0_cost               targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_btone_cost                targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_STAR_accent_cost          targ_seg cand_seg))))
(set! cost (+ cost (* 999 (expro_blacklisted_cost         targ_seg cand_seg))))
(set! cost (* gtcw (/ cost (+ 10 5 5 6 7 4 3 5 10 25 32 32))))

cost)

(define (expro_target_cost_star_noemph targ_seg cand_seg)
"
(expro_target_cost_star_noemph targ_seg cand_seg)
The defaut target cost components, plus
32 * expro_btone_cost
32 * expro_star_accent_cost (for the 2-way classifier: +-accented)

Usage: (du_voice.setTargetCost VOICE expro_target_cost_star_noemph)
"
(set! cost 0)
(set! cost (+ cost (* 10 (expro_stress_cost               targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_position_in_syllable_cost targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_position_in_word_cost     targ_seg cand_seg))))
(set! cost (+ cost (*  6 (expro_partofspeech_cost         targ_seg cand_seg))))
(set! cost (+ cost (*  7 (expro_position_in_phrase_cost   targ_seg cand_seg))))
(set! cost (+ cost (*  4 (expro_left_context_cost         targ_seg cand_seg))))
(set! cost (+ cost (*  3 (expro_right_context_cost        targ_seg cand_seg))))
(set! cost (+ cost (*  5 (expro_inner_context_cost        targ_seg cand_seg))))
(set! cost (+ cost (* 10 (expro_bad_duration_cost         targ_seg cand_seg))))
(set! cost (+ cost (* 25 (expro_bad_f0_cost               targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_btone_cost                targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_star_accent_cost          targ_seg cand_seg))))
(set! cost (+ cost (* 999 (expro_blacklisted_cost         targ_seg cand_seg))))
(set! cost (* gtcw (/ cost (+ 10 5 5 6 7 4 3 5 10 25 32 32))))

cost)

(define (expro_target_cost_slim1  targ_seg cand_seg)
"
(expro_target_cost_slim1 targ_seg cand_seg)

Only expro_bad_duration_cost
     expro_bad_f0_cost
     expro_emph_cost
     expro_btone_cost
     
Usage: (du_voice.setTargetCost VOICE expro_target_cost_slim1)
"
(set! cost 0)
(set! cost (+ cost (* 10 (expro_bad_duration_cost         targ_seg cand_seg))))
(set! cost (+ cost (* 25 (expro_bad_f0_cost               targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_emph_cost                 targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_btone_cost                targ_seg cand_seg))))
(set! cost (+ cost (* 999 (expro_blacklisted_cost          targ_seg cand_seg))))
(set! cost (* gtcw (/ cost (+ 10 25 32 32))))

cost)

(define (expro_target_cost_slim2  targ_seg cand_seg)
"
(expro_target_cost_slim2 targ_seg cand_seg)

Only expro_stress_cost
     expro_bad_duration_cost
     expro_bad_f0_cost
     expro_emph_cost
     expro_btone_cost
     
Usage: (du_voice.setTargetCost VOICE expro_target_cost_slim2)
"
(set! cost 0)
(set! cost (+ cost (* 10 (expro_stress_cost               targ_seg cand_seg))))
(set! cost (+ cost (* 10 (expro_bad_duration_cost         targ_seg cand_seg))))
(set! cost (+ cost (* 25 (expro_bad_f0_cost               targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_emph_cost                 targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_btone_cost                targ_seg cand_seg))))
(set! cost (+ cost (* 999 (expro_blacklisted_cost          targ_seg cand_seg))))
(set! cost (* gtcw (/ cost (+ 10 10 25 32 32))))

cost)

(define (expro_target_cost_slim3  targ_seg cand_seg)
"
(expro_target_cost_slim3 targ_seg cand_seg)

Only expro_partofspeech_cost
     expro_bad_duration_cost
     expro_bad_f0_cost
     expro_emph_cost
     expro_btone_cost
     
Usage: (du_voice.setTargetCost VOICE expro_target_cost_slim3)
"
(set! cost 0)
(set! cost (+ cost (* 10 (expro_partofspeech_cost         targ_seg cand_seg))))
(set! cost (+ cost (* 10 (expro_bad_duration_cost         targ_seg cand_seg))))
(set! cost (+ cost (* 25 (expro_bad_f0_cost               targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_emph_cost                 targ_seg cand_seg))))
(set! cost (+ cost (* 32 (expro_btone_cost                targ_seg cand_seg))))
(set! cost (+ cost (* 999 (expro_blacklisted_cost          targ_seg cand_seg))))
(set! cost (* gtcw (/ cost (+ 10 10 25 32 32))))

cost)


(define (expro_target_cost_off  targ_seg cand_seg)
"
(expro_target_cost_off targ_seg cand_seg)

Only expro_bad_duration_cost
     expro_bad_f0_cost

No normalisation to 0..1!
     
Usage: (du_voice.setTargetCost VOICE expro_target_cost_off)
"
(set! cost 0)
(set! cost (+ cost (* 10 (expro_bad_duration_cost         targ_seg cand_seg))))
(set! cost (+ cost (* 25 (expro_bad_f0_cost               targ_seg cand_seg))))

cost)



(provide 'expro_target_cost)
