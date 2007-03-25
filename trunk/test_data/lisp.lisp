;Comments about this file
;Some lisp for working with DNA sequences


(defun complement-base (b)
  (cond
   ((eq b 'A) 'T)
   ((eq b 'T) 'A)
   ((eq b 'G) 'C)
   ((eq b 'C) 'G)
   (t nil)
  )
)

(defun complement-strand (dna)
  (cond
   ((null dna) nil)
   (t (cons (complement-base (car dna)) (complement-strand (cdr dna))))
  )
)

(defun make-double (dna)
  (cond
   ((null dna) nil)
   (t (cons (list (car dna) (complement-base (car dna)))
            (make-double (cdr dna)))
   )
  )
)

(defun countbases (dna)
  (setf cntA 0)
  (setf cntT 0)
  (setf cntG 0)
  (setf cntC 0)
  (cond
   ((null dna) nil)
   ((atom (car dna)) (count-bases dna)) ;Single Stranded DNA
   (t (dolist (next dna) ;Double Stranded DNA
        (cond
         ((or (eq (car next) 'A) (eq (car next) 'T)) 
                             (setf cntA (incf cntA))
                             (setf cntT (incf cntT)))
         ((or (eq (car next) 'G) (eq (car next) 'C)) 
                             (setf cntG (incf cntG))
                             (setf cntC (incf cntC)))
         (t nil)
        )
      )
      (list (list 'A cntA) (list 'T cntT)
            (list 'G cntG) (list 'C cntC))
  )
 )
)

(defun count-bases (dna)
  (cond
   ((null dna) nil)
   (t (dolist (next dna)
        (cond
         ((eq next 'A) (setf cntA (incf cntA)))
         ((eq next 'T) (setf cntT (incf cntT)))
         ((eq next 'G) (setf cntG (incf cntG)))
         ((eq next 'C) (setf cntC (incf cntC)))
         (t nil)
        )
      )
      (list (list 'A cntA) (list 'T cntT)
            (list 'G cntG) (list 'C cntC))
   )
  )
)

(defun prefixp (dna1 dna2)
  (cond
   ((null dna1) t)
   ((eq (car dna1) (car dna2)) (prefixp (cdr dna1) (cdr dna2)))
   (t nil)
  )
)

(defun appearsp (dna1 dna2)
  (cond
   ((null dna1) t)
   ((null dna2) nil)
   ((prefixp dna1 dna2) t)
   (t (appearsp dna1 (cdr dna2)))
  )
)

(defun coverp (dna1 dna2)
  (cond
   ((null dna2) t)
   ((prefixp dna1 dna2) (coverp dna1 (nthcdr (length dna1) dna2)))
   (t nil)
  )
)

(defun prefix (x dna)
  (cond
   ((eq x 0) nil)
   (t (butlast dna (- (length dna) x)))
  )
)

(defun kernel (dna)
  (cond
   ((null dna) nil)
   (t (kernel-help dna 1))
  )
)

(defun kernel-help (dna x)
  (cond
   ((eq x (length dna)) dna)
   ((coverp (prefix x dna) dna) (prefix x dna))
   (t (kernel-help dna (+ 1 x)))
  )
)
