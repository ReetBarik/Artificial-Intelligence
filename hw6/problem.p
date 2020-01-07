fof(a1, axiom,
	! [X] : (like(X, computers) => like(X, coding))).

fof(a2, axiom, 
	! [X] : ((like(X, coding) & like(X, chess)) => learn(X, ai))).

fof(a3, axiom,
	! [X] : (learn(X, ai) => ? [Y] : (hire(Y, X)))).

fof(a4, axiom,
	! [X] : (
	? [Y] : (hire(Y, X)) => (rich(X) & famous(X)))).

fof(a5, axiom, like(larry, computers)).

fof(a6, axiom, like(larry, chess)). 

fof(c1, conjecture, rich(larry)).