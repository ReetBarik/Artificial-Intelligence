// Agent.cc
//
// Solution to HW2. Written by Larry Holder.

#include <iostream>
#include "Agent.h"

using namespace std;

Agent::Agent ()
{

}

Agent::~Agent ()
{

}

void Agent::Initialize ()
{
	worldState.agentLocation = Location(1,1);
	worldState.agentOrientation = RIGHT;
	worldState.agentHasGold = false;
	worldState.agentAlive = true;
	worldState.agentHasArrow = true;
	worldState.agentInCave = true;
	worldState.wumpusAlive = true;
	safeColumn = 0; // i.e., don't know
	agentGoal = MOVERIGHT;
	lastAction = CLIMB; // dummy action to start
	
}

Action Agent::Process (Percept& percept)
{
	Action action;
	updateState(lastAction,percept);
	int X = worldState.agentLocation.X;
	int Y = worldState.agentLocation.Y;
	Orientation orientation = worldState.agentOrientation;
	
	switch (agentGoal) {
	
	case MOVERIGHT: // Move right along row 1 looking for safe column
		if (percept.Stench || percept.Breeze) {
			action = GOFORWARD;
		} else {
			// X column is safe
			action = TURNLEFT;
			agentGoal = MOVEUP;
			safeColumn = X;
		}
		break;
		
	case MOVEUP:
		if (Y < 3) {
			action = GOFORWARD;
		} else {
			if (X < 3) {
				agentGoal = FINDGOLD;
			} else {
				action = TURNLEFT;
				agentGoal = MOVELEFT;
			}
		}
		break;
		
	case MOVELEFT:
		if (X > 2) {
			action = GOFORWARD;
		} else {
			agentGoal = FINDGOLD;
		}
		break;
		
	case MOVEDOWN: // Move to safe column, and then down to row 1
		if (Y == 1) {
			action = TURNRIGHT;
			agentGoal = LEAVE;
		} else if (X == safeColumn) {
			if (orientation == DOWN) {
				action = GOFORWARD;
			} else {
				action = TURNRIGHT;
			}
		} else if (X < safeColumn) {
			if (orientation == RIGHT) {
				action = GOFORWARD;
			} else {
				action = TURNRIGHT;
			}
		} else { // X > safeColumn
			if (orientation == LEFT) {
				action = GOFORWARD;
			} else {
				action = TURNRIGHT;
			}
		}
		break;
		
	case LEAVE: // Agent in row 1 facing LEFT
		if ((X == 1) && (Y == 1)) {
			action = CLIMB;
		} else {
			action = GOFORWARD;
		}
		break;
		
	case FINDGOLD:
		break; // Handle outside switch
	}
	
	if (agentGoal == FINDGOLD) {
		// Follow CW route until find gold
		if (percept.Glitter) {
			action = GRAB;
			agentGoal = MOVEDOWN;
		} else {
			// Move to next potential gold location
			if ((X == 1) && (Y == 3)) {
				if (orientation == UP) {
					action = GOFORWARD;
				} else {
					// Must be LEFT
					action = TURNRIGHT;
				}
			} else if ((X == 1) && (Y == 4)) {
				if (orientation == RIGHT) {
					action = GOFORWARD;
				} else {
					// Must be UP
					action = TURNRIGHT;
				}
			} else if ((X == 2) && (Y == 4)) {
				if (orientation == DOWN) {
					action = GOFORWARD;
				} else {
					// Must be RIGHT
					action = TURNRIGHT;
				}
			} else { // Must be in (2,3)
				if (orientation == LEFT) {
					action = GOFORWARD;
				} else {
					// Must be DOWN
					action = TURNRIGHT;
				}
			}
		}
	}
	
	lastAction = action;
	return action;
}

void Agent::GameOver (int score)
{

}

void Agent::updateState(Action lastAction, Percept& percept) {
	int X = worldState.agentLocation.X;
	int Y = worldState.agentLocation.Y;
	Orientation orientation = worldState.agentOrientation;
	
	if (lastAction == TURNLEFT) {
		worldState.agentOrientation = (Orientation) ((orientation + 1) % 4);
	}
	if (lastAction == TURNRIGHT) {
		if (orientation == RIGHT) {
			worldState.agentOrientation = DOWN;
		} else {
			worldState.agentOrientation = (Orientation) (orientation - 1);
		}
	}
	if ((lastAction == GOFORWARD) && (! percept.Bump)) {
		switch (orientation) {
		case UP:
			worldState.agentLocation.Y = Y + 1;
			break;
		case DOWN:
			worldState.agentLocation.Y = Y - 1;
			break;
		case LEFT:
			worldState.agentLocation.X = X - 1;
			break;
		case RIGHT:
			worldState.agentLocation.X = X + 1;
			break;
		}
	}
	if (lastAction == GRAB) { // Assume GRAB only done if Glitter was present
			worldState.agentHasGold = true;
	}
	if (lastAction == SHOOT) {
		worldState.agentHasArrow = false;
		if (percept.Scream) {
			worldState.wumpusAlive = false;
		}
	}
	if (lastAction == CLIMB) { 
		// do nothing; if CLIMB worked, this won't be executed anyway
	}
}
