;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;                                                                       ;;
;;;                Centre for Speech Technology Research                  ;;
;;;                     University of Edinburgh, UK                       ;;
;;;                       Copyright (c) 2015                              ;;
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
;;; Multisyn hybrid top level scheme code  (Rob Clark)
;;;

; Requires
(require_module 'MultiSyn)
(require 'multisyn)
(require 'target_cost)
(require 'hts)

;; Needs a real value once finished
(defvar target_coefs_progname "/Users/robert/tmp/fakeit")

;; This current uses HTS to dump label files, DNN based (external sourse) bottleneck target cost features 
;;   and multisyn unit selection
(defSynthType MultiSyn_Hybrid
  (defvar hts_featfile (make_tmp_filename))
  (defvar hts_mcepfile (make_tmp_filename))
  (defvar hts_f0file (make_tmp_filename))
  (defvar hts_wavfile (make_tmp_filename))
  (defvar hts_labfile (make_tmp_filename))
  (defvar hybrid_targetcoeffile (make_tmp_filename))


  (Param.def "unisyn.window_name" "hanning")
  (Param.def "unisyn.window_factor" 1.0)
  ;; Unisyn requires these to be set.
  (set! us_abs_offset 0.0)
  (set! us_rel_offset 0.0)

  (apply_hooks hts_synth_pre_hooks utt)
  (set! hts_output_params
    (list
     (list "-labelfile" hts_featfile)
     (list "-om" hts_mcepfile)
     (list "-of" hts_f0file)
     (list "-or" hts_wavfile)
     (list "-od" hts_labfile)
     (list "-requireStateTimesOut" 1))
    )
  (hts_dump_feats utt hts_feats_list hts_featfile)
  (HTS_Synthesize utt)

  (apply_hooks MultiSyn_module_hooks utt)  ;; 4processing of diphone names
  
  (format stderr "labfile: %s\n" hts_labfile)

  (multisyn_hybrid_create_target_coefs hts_labfile hybrid_targetcoeffile)  
  (multisyn_hybrid_fill_target_coefficients currentMultiSynVoice utt hybrid_targetcoeffile)


  ;; find appropriate unit sequence and put sythesis
  ;; parameters in the Unit relation of the utterance structure
  (voice.getUnits currentMultiSynVoice utt)
  
  ;(print "doing concat")
  (us_unit_concat utt)

  ;(print "doing raw concat")

  (utt.relation.create utt 'SourceSegments)

  (set! do_prosmod (du_voice.prosodic_modification currentMultiSynVoice))

  (if do_prosmod
      (begin
  (if (not (member 'f0 (utt.relationnames utt)))
      (targets_to_f0 utt))
  ;; temporary fix
  (if (utt.relation.last utt 'Segment)
      (set! pm_end (+ (item.feat (utt.relation.last utt 'Segment) "end") 0.02))
      (set! pm_end 0.02))
  (us_f0_to_pitchmarks  utt 'f0 'TargetCoef pm_end)
  (us_mapping utt 'segment_single))
      (begin
  (utt.copy_relation utt 'SourceCoef 'TargetCoef)
  (us_mapping utt "linear")))


  ;(print "generating wave")
;; specify something else if you don't want lpc
  (us_generate_wave utt 'lpc)


  (apply_hooks hts_synth_post_hooks utt)  
  
  (delete-file hts_featfile)
  (delete-file hts_mcepfile)
  (delete-file hts_f0file)
  (delete-file hts_wavfile)
  (delete-file hts_labfile)
  (delete-file hybrid_targetcoeffile)
    utt)

;;; Hybrid support functions
(define (multisyn_hybrid_create_target_coefs featfile targetcoeffile)
  "(multisyn_hybrid_create_target_coefs featfile targetcoeffile)
  External system call to create targetcost cooeficients for utterance."
  (system (format nil "%s %s %s" target_coefs_progname featfile targetcoeffile)))

(provide 'multisyn_hybrid)

