// Agent.h
//
// Solution to HW2. Written by Larry Holder.

#ifndef AGENT_H
#define AGENT_H

#include "Action.h"
#include "Percept.h"

#include "WorldState.h"

enum AgentGoal { MOVERIGHT, MOVEUP, MOVELEFT, FINDGOLD, MOVEDOWN, LEAVE };

class Agent
{
public:
	Agent ();
	~Agent ();
	void Initialize ();
	Action Process (Percept& percept);
	void GameOver (int score);
	
	void updateState(Action lastAction, Percept& percept);
	
	WorldState worldState;
	int safeColumn; // If no wumpus or pit in row 2 column C, then set this to C; otherwise 0
	AgentGoal agentGoal;
	Action lastAction;
	
};

#endif // AGENT_H
