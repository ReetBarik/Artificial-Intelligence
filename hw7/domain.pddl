(define (domain VACUUM)
	(:predicates
		(room ?r)
		(dirty ?r)
		(clean ?r)
	)
	(:action left
		:precondition (room B)
		:effect (and (not (room B)) (room A))
	)
	(:action right
		:precondition (room A)
		:effect (and (not (room A)) (room B))
	)
	(:action suck
		:parameters (?r)
		:precondition (and (not (clean ?r)) (room ?r))
		:effect (clean ?r)
	)
)