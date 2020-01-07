# -*- coding: utf-8 -*-
"""
Created on Sun Sep 1 00:35:57 2019

@author: Reet Barik
"""

# PyAgent.py

import Action
import Orientation
import random

class Agent:
    def __init__(self):
        self.current_orientation = Orientation.RIGHT # orientation of the agent; will be handy to calc location of agent
        self.location = [1,1] # location of the agent
        self.gold_grabbed = False # Check if gold is with the agent
        self.glitterCheck = 0 # Found gold or not
        self.actionList = [] # For taking actions in succession
        self.move = [] # For creating moves to add to action list
        self.trace_path = [] # To keep a track of the path taken to the gold

    def decide_orientation (self, add_direction):
        self.current_orientation += add_direction
        if self.current_orientation > 3: # taking left from down will become right
            self.current_orientation -= 4
        if self.current_orientation < 0: # taking right from right will become down
            self.current_orientation += 4

    # moves are reversed because they will pop()
    def create_move_right (self):
        self.move = [ Action.GOFORWARD, Action.TURNRIGHT]
        self.trace_path.extend([ Action.TURNLEFT, Action.GOFORWARD]) # For tracing back path when gold is found

    def create_move_left (self):
        self.move = [ Action.GOFORWARD, Action.TURNLEFT]
        self.trace_path.extend([ Action.TURNRIGHT, Action.GOFORWARD]) # For tracing back path when gold is found

    def create_move_turnAround (self):
        self.move = [ Action.TURNRIGHT, Action.TURNRIGHT] # For turning take two rights

    def add_shoot (self):
        self.move.insert( len(self.move)-1, Action.SHOOT) # turn left, shoot and move forward

    def optimize_traced_path (self):
        if self.glitterCheck == 3:
            # In the case of a loop
            self.trace_path = self.trace_path[0:-5] # remove path instead retracing loop 
            
            # In the row 3
            if self.location[1] > 2:
               
                if (len(self.trace_path) > 5) or (len(self.trace_path) < 5 and self.location[1]==3):
                    
                    self.trace_path.pop()
                    self.create_move_left()
                    self.trace_path = self.trace_path[0:-2]
                    self.trace_path.extend(self.move)
                    self.create_move_right()
                    self.trace_path = self.trace_path[0:-2]
                    self.trace_path.extend(self.move)

                else:
                    self.trace_path.insert(-2,Action.GOFORWARD)

                # Remove extra move - the turn agent made while starting from (1,1) 
                if self.trace_path[0] > 0:
                    self.trace_path.pop(0)

                # Add the path backwards to the actionList
                self.actionList = agent.trace_path
                
        else:
            # No loop so turn around and head back
            self.create_move_turnAround()

            # Remove extra move - the turn agent made while starting from (1,1)
            if self.trace_path[0] > 0:
                self.trace_path.pop(0)
            self.actionList = agent.trace_path
            self.actionList.extend(agent.move)

    # Update agent's location based on orientation on Action.GOFORWARD
    def update_location (self):
        if self.current_orientation == Orientation.UP:
            self.location[1] += 1
        elif self.current_orientation == Orientation.DOWN:
            self.location[1] -= 1
        elif self.current_orientation == Orientation.RIGHT:
            self.location[0] += 1
        else:
            self.location[0] -= 1

def PyAgent_Constructor ():
    print("PyAgent_Constructor")

def PyAgent_Destructor ():
    print("PyAgent_Destructor")

def PyAgent_Initialize ():

    global agent # To make agent Object of class Agent available in PyAgent_Process
    agent = Agent()
    print("PyAgent_Initialize")

def PyAgent_Process (stench,breeze,glitter,bump,scream):

    
    If we want to keep a track if the wumpus died
    if scream == True:
        agent.wumpus_killed = True

    if not agent.actionList:

        if agent.gold_grabbed == True:
            # If gold grabbed then trace back path to climb back

            if agent.location == [1,1]:
                agent.actionList = [Action.CLIMB]
            else:
                # Optimize the path to take backwards and add all actions to actionList
                agent.optimize_traced_path()


        elif glitter == True:
            # If glitter then grab gold
            agent.actionList = [Action.GRAB]
            agent.gold_grabbed = True


        elif bump == True:
            dir = random.randint(0, 1)
            if dir == 0:
                agent.create_move_left()
                agent.actionList.extend(agent.move)
            else:
                agent.create_move_right()
                agent.actionList.extend(agent.move)
        
        elif agent.location[1] == 1:      # We are in row 1
            
            # If breeze keep moving right
            if breeze == False:
                # If stench then decide to kill wumpus
                if stench == True:
                    
                    agent.create_move_left()
                    agent.add_shoot()
                    agent.actionList.extend(agent.move)

                # If no breeze then move left
                else:
                    agent.create_move_left()
                    agent.actionList.extend(agent.move)
            
            # there is breeze then keep going right to avoid pit
            else:
                agent.actionList.append(Action.GOFORWARD)
                agent.trace_path.append(Action.GOFORWARD)
        
        # Agent in row 2 and obviously facing upwards
        elif agent.location[1] == 2:
            agent.actionList.append(Action.GOFORWARD)
            agent.trace_path.append(Action.GOFORWARD)
        
        # Agent in row 3 but in location 3,3 or 4,3; So make it travel to 2,3
        elif agent.location[0]>2:
            if agent.current_orientation == Orientation.UP:
                agent.create_move_left()
                agent.actionList.extend(agent.move)
            else:
                agent.actionList.append(Action.GOFORWARD)
                agent.trace_path.append(Action.GOFORWARD)
        
        # Now it will go looking for gold in a clockwise manner

        # Agent in location 2,3
        elif agent.location == [2,3]:
            agent.glitterCheck += 1

            # If facing up then move left (turn left and go forward)
            if agent.current_orientation == Orientation.UP:
                agent.create_move_left()
                agent.actionList.extend(agent.move)

            # If facing left then just go forward
            elif agent.current_orientation == Orientation.LEFT:
                agent.actionList.append(Action.GOFORWARD)
                agent.trace_path.append(Action.GOFORWARD)
        
        # Agent in location 1,3
        elif agent.location == [1,3]:
            agent.glitterCheck += 1

            # If facing left then move right (turn right and go forward)
            if agent.current_orientation == Orientation.LEFT:
                agent.create_move_right()
                agent.actionList.extend(agent.move)

            # If facing up then just go forward
            elif agent.current_orientation == Orientation.UP:
                agent.actionList.append(Action.GOFORWARD)
                agent.trace_path.append(Action.GOFORWARD)
        
        # Agent in location 1,4
        elif agent.location == [1,4]:
            agent.glitterCheck += 1

            # move right (turn right as it is facing upward and go forward)
            agent.create_move_right()
            agent.actionList.extend(agent.move)

        # Agent in location 2,4
        elif agent.location == [2,4]:
            agent.glitterCheck += 1

            # move down (turn right as it is facing right and go forward)
            agent.create_move_right()
            agent.actionList.extend(agent.move)

    
    action = agent.actionList.pop()
    if action == Action.GOFORWARD:
        agent.update_location() # Whenever agent goes forward then only location changes
    elif action == Action.TURNLEFT:
        agent.decide_orientation(1) # add 1 to orientation on taking left
    elif action == Action.TURNRIGHT:
        agent.decide_orientation(-1) # add -1 to orientation on taking right

    return action

def PyAgent_GameOver (score):
    print("PyAgent_GameOver: score = " + str(score))
