
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
(define (dump_costs . args)
  "(dump_costs UTT) or (dump_costs UTT FN)

Print target and join costs (to the previous diphone, i.e. the first 
one is always 0) of selected units plus where they come from
(utterance name, end time of left half-phone, start time of the left  
half phone i.e. of the diphone, and end time of the right half phone 
i.e. the diphone (the latter two times are calculated according to the
formula in DiphoneVoiceModule.cc).

Unless a file name is given, they are printed to stdout.

The selected segments items are put in a global list variable \"sl\" 
for more convenient access, e.g. print features of first segment 

    (item.features (nth 0 sl))

The word(s) a segment comes from is/are printed as well as context 
words if possible.  If the 'star_accent feature is set to 1 or 0.5, 
the word is marked up with an asterik or a plus sign resp.  If the 
'emph feature is set to 1, a hash sign is added.
"
(let (utt fn fd s w ps pw ns wrd si ljt ss rjt)
   (cond
      ((eqv? 1 (length args))
         (set! utt (nth 0 args))
         (set! fn nil)
         (set! fd  t))
      ((eqv? 2 (length args))
         (set! utt (nth 0 args))
         (set! fn  (nth 1 args))
         (set! fd  (fopen fn "w")))
      (t
         (error "usage: (dump_costs UTT) or (dump_costs UTT FN)")))
   
   (set! sl nil) ; list of souce segment items
   (set! si 0)   ; index of souce segment item

   
   (format fd "#         target_c  join_cost     src_utt    pho_end  di_start di_end  \n")
   (mapcar
      (lambda(u)
         (set! s (item.feat u 'source_ph1))
         (if(eqv? s 0)(error "dump_costs: feature source_ph1 undefined"))
         (set! w (item.parent (item.parent(item.relation s 'SylStructure))))
   
         (if w
            (begin
               (set! ps (item.prev s))
               (set! pw (item.parent (item.parent(item.relation ps 'SylStructure))))
               (set! ns (item.next s))
               (set! nw (item.parent (item.parent(item.relation ns 'SylStructure))))
               (set! wrd (item.name w))
               (if(not(equal? 0 (item.feat s 'btone)))
                  (set! wrd (string-append wrd (item.feat s 'btone))))
               (if (equal? 1 (item.feat s 'star_accent))
                  (set! wrd (string-append "*" wrd)))
               (if (equal? 0.5 (item.feat s 'star_accent))
                  (set! wrd (string-append "+" wrd)))
               (if (equal? 1 (item.feat s 'emph))
                  (set! wrd (string-append "#" wrd)))
               (if pw
                  (begin
                     (if(not(equal? w pw))
                        (set! wrd (string-append (item.name pw) "_" wrd)))
                     (if(item.prev pw)
                        (set! wrd(string-append "(" (item.name(item.prev pw)) ") " wrd))))
                  (if(item.prev w)
                     (set! wrd(string-append "(" (item.name(item.prev w)) ") " wrd))))
               (if nw  
                  (begin
                     (if(not(equal? w nw))
                        (set! wrd (string-append wrd "_" (item.name nw))))
                     (if(item.next nw)
                        (set! wrd(string-append wrd " (" (item.name(item.next nw)) ")"))))
                  (if(item.next w)
                     (set! wrd(string-append wrd " (" (item.name(item.next w)) ")"))))
            )
            (set! wrd ""))
   
         (set! sl (append sl (list s)))
   
         (if(item.feat.present s 'cl_end)
            (set! ljt (item.feat s 'cl_end))
            (if(item.feat.present s 'dipth)
               (set! ljt (+(* 0.75 (item.feat s 'start))(* 0.25 (item.feat s 'end))))
               (set! ljt (/(+(item.feat s 'start)(item.feat s 'end))2))))
         (set! ss (item.next s))
         (if(item.feat.present ss 'cl_end)
            (set! rjt (item.feat ss 'cl_end))
            (if(item.feat.present ss 'dipth)
               (set! rjt (+(* 0.75 (item.feat ss 'start))(* 0.25 (item.feat ss 'end))))
               (set! rjt (/(+(item.feat ss 'start)(item.feat ss 'end))2))))

         (format fd "%8s  %f  %f  %3s %8s %f %f %f (nth %d sl)  %s\n" 
                              (item.name u)
                              (item.feat u 'target_cost)
                              (item.feat u 'join_cost)
                              (item.feat s 'name)
                              (item.feat u 'source_utt)
                              (item.feat s 'end)
                              ljt
                              rjt
                              si
                              wrd)
         (set! si (+ 1 si)))
      (utt.relation.items utt 'Unit))
      (if fn
         (fclose fd)
         (utt.play utt)))
nil)


(provide 'dump_costs)
