
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

(define (detect_quoting utt context)
  "(detect_quoting UTT context)

Marking up of quotes (Token feature squoted), quotes within quotes (feature
dquoted), and all-uppercase (feature upcased).  The value of each feature is 
the length of the token string that is upcased/in single quotes/in double 
quotes, or 0 by default.  These features finally determine emphasis, see
(expro_emphasis utt).

If context is nil, the internal flags within_squoted and within_dquoted are
reset at utterance end.  If context is t, they are not, allowing quotations
spanning several utterances.  The token string length, however, alway refers
to the current utterance.

If context is nil, the internal flags are reset.

Example text:

    `Found IT,' the Mouse said:
    `You know what \"it\" means.'

Token squoted dquoted upcased
`Found  2      0      0
IT'     2      0      1
the     0      0      0
mouse   0      0      0
said.   0      0      0
'You    5      0      0
know    5      0      0
what    5      0      0
\"it\"  5      1      0
means.' 5      0      0


Single-quoted strings 'like this' instead of `like this' are legal, too.

"
(let (token prep punc len)
   (if(null? utt)
      (begin
         (format t "resetting quote detectors\n")
         (set! within_squoted nil)
         (set! within_dquoted nil))
      (begin
         ;;;    F O R   E A C H   T O K E N
         ;;;    ----------------------------
         (set! token (utt.relation.first utt 'Token))
         (while token
            (set! token_name (item.name token))
            ;;;(format t "token name is %l\n" token_name)
            (item.set_feat token "squoted" 0)
            (item.set_feat token "dquoted" 0)
            (item.set_feat token "upcased" 0)
            (set! prep (item.feat token "prepunctuation"))
            (set! punc (item.feat token "punc"))
   
            ;; start of a single-quoted token string?
            (if(or(string-matches prep ".*[`'].*")within_squoted)
               (begin
                  (set! within_squoted t)
                  (set! squoted_tokens (append squoted_tokens (list token)))))
   
            ;; end of a single-quoted token string?
            (if(string-matches punc ".*\'.*")
               (if(null? within_squoted)
                  (format t "warning: nowhere started quotation in single quotes ends at %s\n" token_name)
                  (begin
                     (format t "`%l'\n" (mapcar item.name squoted_tokens))
                     (set! len (length squoted_tokens))
                     (mapcar
                        (lambda(token)
                           (item.set_feat token "squoted" len))
                        squoted_tokens)
                     (set! squoted_tokens nil)
                     (set! within_squoted nil))))
   
            ;; start of a double-quoted token string?
            (if(or(string-matches prep ".*\".*")within_dquoted)
               (begin
                  (set! within_dquoted t)
                  (set! dquoted_tokens (append dquoted_tokens (list token)))))
   
            ;; end of a double-quoted token string?
            (if(string-matches punc ".*\".*")
               (if(null? within_dquoted)
                  (format t "warning: nowhere started quotation in double quotes ends at %s\n" token_name)
                  (begin
                     (format t "````%l''''\n" (mapcar item.name dquoted_tokens))
                     (set! len (length dquoted_tokens))
                     (mapcar
                        (lambda(token)
                           (item.set_feat token "dquoted" len))
                        dquoted_tokens)
                     (set! dquoted_tokens nil)
                     (set! within_dquoted nil))))
   
            (set! word1 (item.relation(item.daughter1 token)'SylStructure))
            (if word1
                (set! nsyls (length(item.daughters word1)))
                (set! nsyls 0))
            ;; is the current token all upper case?
            (if(and(string-matches token_name "[A-Z']+")
                   (>(string-length token_name)1) ;; exclude "I" and spelling
                   (>(string-length token_name)nsyls)) ;; exclude "UK", "BBC" etc. i.e. number
                                                       ;; of letters > number of syls
               (begin
                  ;;(format t "detect_quoting: %s all upper case\n" token_name)
                  (set! upcased_tokens (append upcased_tokens (list token))))
               (begin
                  ;;(format t "detect_quoting: %s no longer upper case\n" token_name)
                  (set! len (length upcased_tokens))
                  (mapcar
                     (lambda(token)
                        (item.set_feat token "upcased" len))
                     upcased_tokens)
                  (set! upcased_tokens nil))
               )
   
      
            (set! token (item.next token))) ;;; end_while token
   
         ;;      U T T E R A N C E   E N D
         ;;      -------------------------
         ;; quotation in single quotes goes beyond this utterance
         (if within_squoted
            (begin
               (format t "`%l'\n" (mapcar item.name squoted_tokens))
               (set! len (length squoted_tokens))
               (mapcar
                  (lambda(token)
                     (item.set_feat token "squoted" len))
                  squoted_tokens)
               (set! squoted_tokens nil)))
   
         ;; quotation in double quotes goes beyond this utterance
         (if within_dquoted
            (begin
               (format t "````%l''''\n" (mapcar item.name dquoted_tokens))
               (set! len (length dquoted_tokens))
               (mapcar
                  (lambda(token)
                     (item.set_feat token "dquoted" len))
                  dquoted_tokens)
               (set! dquoted_tokens nil)))
   
         ;; string of upcased token reaches until utterance end
         (begin
            (set! len (length upcased_tokens))
            (mapcar
               (lambda(token)
                  (item.set_feat token "upcased" len))
               upcased_tokens)
            (set! upcased_tokens nil))
   
   
         (if(null? context)
            (begin
               ;;(format t "... and resetting internal flags\n");!!!
               (if within_squoted
                  (begin
                     (set! within_squoted nil)
                     (format t "utterance ends while still within a quotation in single quotes\n")))
               (if within_dquoted
                  (begin
                     (set! within_dquoted nil)
                     (format t "utterance ends while still within a quotation in double quotes\n")))))))))



(set! squoted_tokens nil) (set! within_squoted nil)
(set! dquoted_tokens nil) (set! within_dquoted nil)
(set! upcased_tokens nil)

(provide 'detect_quoting)
