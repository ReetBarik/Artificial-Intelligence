(define (problem prob)
	(:domain VACUUM)
	(:objects A B)
 	(:init (room A) (dirty A) (dirty B))
 	(:goal (and (clean A) (clean B)))
) 