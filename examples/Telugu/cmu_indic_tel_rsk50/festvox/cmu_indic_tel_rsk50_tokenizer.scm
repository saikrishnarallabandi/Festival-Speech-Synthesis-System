;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;                                                                     ;;;
;;;                     Carnegie Mellon University                      ;;;
;;;                  and Alan W Black and Kevin Lenzo                   ;;;
;;;                      Copyright (c) 1998-2000                        ;;;
;;;                        All Rights Reserved.                         ;;;
;;;                                                                     ;;;
;;; Permission is hereby granted, free of charge, to use and distribute ;;;
;;; this software and its documentation without restriction, including  ;;;
;;; without limitation the rights to use, copy, modify, merge, publish, ;;;
;;; distribute, sublicense, and/or sell copies of this work, and to     ;;;
;;; permit persons to whom this work is furnished to do so, subject to  ;;;
;;; the following conditions:                                           ;;;
;;;  1. The code must retain the above copyright notice, this list of   ;;;
;;;     conditions and the following disclaimer.                        ;;;
;;;  2. Any modifications must be clearly marked as such.               ;;;
;;;  3. Original authors' names are not deleted.                        ;;;
;;;  4. The authors' names are not used to endorse or promote products  ;;;
;;;     derived from this software without specific prior written       ;;;
;;;     permission.                                                     ;;;
;;;                                                                     ;;;
;;; CARNEGIE MELLON UNIVERSITY AND THE CONTRIBUTORS TO THIS WORK        ;;;
;;; DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING     ;;;
;;; ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT  ;;;
;;; SHALL CARNEGIE MELLON UNIVERSITY NOR THE CONTRIBUTORS BE LIABLE     ;;;
;;; FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES   ;;;
;;; WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN  ;;;
;;; AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,         ;;;
;;; ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF      ;;;
;;; THIS SOFTWARE.                                                      ;;;
;;;                                                                     ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;
;;; Tokenizer for indic
;;;
;;;  To share this among voices you need to promote this file to
;;;  to say festival/lib/cmu_indic/ so others can use it.
;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;; Load any other required files

;; Punctuation for the particular language
(set! cmu_indic_tel_rsk50::token.punctuation "") ; \"'`.,:;!?(){}[]")
(set! cmu_indic_tel_rsk50::token.prepunctuation "") ; "\"'`({[")
(set! cmu_indic_tel_rsk50::token.whitespace " \t\n\r")
(set! cmu_indic_tel_rsk50::token.singlecharsymbols "")

(define (unicode_class c)
  (cond
   ((member_string c
    '("\"" "'" "`" "." "," ":" ";" "!" "?" "(" ")" "{" "}" "[" "]" "-"
      "।" ;; hindi full stop
      ))
    'punc)
   ((member_string c
    '("_" "+" "=" "~" "/" "|" "\\" "<" ">" "@" "#" "$" "%" "^" "&" "*"))
    'symbol)
   ((member_string c '("0" "1" "2" "3" "4" "5" "6" "7" "8" "9"))
    'digit)
   (t
    'word)))

(define (unicode_string_segment name)
  ;; Segments the content of the unicode name string into type
  ;; segments -- word class characters are concatenated all others
  ;; are treated as single character symboles
  ;; (unicode_string_segment "hello-world,")  becomes
  ;; ((word "hello") (punc "-") (word "world") (punc ","))
  (let ((unc (utf8explode name))
        (ws nil) (w nil) (uclass nil))

    (while unc
     (set! uclass (unicode_class (car unc)))
     (cond
      ((string-equal 'word uclass)
       (set! w (cons (car unc) w)))
      (t  ;; anything else causes a word boundary (maybe not right for digits)
       (if w
           (set! ws (cons (list 'word (apply string-append (reverse w))) ws)))
       (set! ws (cons (list uclass (car unc)) ws))
       (set! w nil)))
     (set! unc (cdr unc)))
    (if w
        (set! ws (cons (list 'word (apply string-append (reverse w))) ws)))
    (reverse ws)
))


;;; Voice/indic token_to_word rules 
(define (cmu_indic_tel_rsk50::token_to_words token name)
  "(cmu_indic_tel_rsk50::token_to_words token name)
Specific token to word rules for the voice cmu_indic_tel_rsk50.  Returns a list
of words that expand given token with name."
 (cond
   ((string-matches name "^[0-9a-zA-Z/:_-]+$")
    (english_token_to_words token name))
   (t
(let ((unicode_tokens (unicode_string_segment name))
        (words nil))

    (mapcar
     (lambda (tok)
       (cond
        ((string-equal 'punc (car tok))
         t) ;; doesn't result in a word
        (t
         (set! words (cons (cadr tok) words)))))
     unicode_tokens)
    (set! words (reverse words))

;    (format t "Token: %l to words %l tokens %l\n"
;            name words unicode_tokens)

    (cond
     ((and unicode_tokens (null (cdr unicode_tokens))
           (string-equal 'punc (caar unicode_tokens))
           (item.prev token))
      ;; One symbol, just a punctuation, and there is a prev token
      (item.set_feat (item.prev token) "punc" ","))
     ((string-equal 'punc (caar (reverse unicode_tokens)))
      ;; if last segment is a punctuation, add break
      (item.set_feat token "punc" ","))
     (t
      t))

    words))))


(define (cmu_indic::number token name)
  "(cmu_indic::number token name)
Return list of words that pronounce this number in indic."

  (error "cmu_indic::number to be written\n")

)

(define (cmu_indic_tel_rsk50::select_tokenizer)
  "(cmu_indic_tel_rsk50::select_tokenizer)
Set up tokenizer for indic."
  (Parameter.set 'Language 'cmu_indic)
  (set! token.punctuation cmu_indic_tel_rsk50::token.punctuation)
  (set! token.prepunctuation cmu_indic_tel_rsk50::token.prepunctuation)
  (set! token.whitespace cmu_indic_tel_rsk50::token.whitespace)
  (set! token.singlecharsymbols cmu_indic_tel_rsk50::token.singlecharsymbols)

  (set! token_to_words cmu_indic_tel_rsk50::token_to_words)
)

(define (cmu_indic_tel_rsk50::reset_tokenizer)
  "(cmu_indic_tel_rsk50::reset_tokenizer)
Reset any globals modified for this voice.  Called by 
(cmu_indic_tel_rsk50::voice_reset)."
  ;; None

  t
)

(provide 'cmu_indic_tel_rsk50_tokenizer)
