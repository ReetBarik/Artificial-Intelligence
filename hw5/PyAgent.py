# PyAgent.py

import random
import sys
import Action
import Orientation


class Agent:
    def __init__(self):
        self.agentHasGold = False
        self.strategy = Strategy()
        self.takeRisk = 0
        self.agentHasGold = False
        self.actions = []
        self.currentLocation = [1,1]
        self.destination = [1,1]
        self.currentOrientation = Orientation.RIGHT
        self.explored = [[1,1]]
        self.goldLocation = []
        self.strategy.addSafeLocation(1,1)
    
    def Initialize(self):
        self.actions = []
        self.agentHasGold = False
        if self.currentLocation != [1,1]:
            self.strategy.removeSafeLocation(self.currentLocation[0],self.currentLocation[1])
            self.takeRisk = 0
            self.explored.append(self.currentLocation)
            self.currentLocation = [1,1]
            self.currentOrientation = Orientation.RIGHT
        elif self.goldLocation!=[]:
            self.currentOrientation = Orientation.RIGHT
            self.actions = self.strategy.findPath(self.currentLocation, self.currentOrientation, self.goldLocation, Orientation.RIGHT)

    # Find a safe unvisited location
    def whereNext(self):
        # Sequentially check locations which might be safe to go to. If no safe location avialble then take risk
        for j in range(1,5):
            for i in range(1,5):
                destination = [i,j]
                if [i,j] not in self.explored:
                    if [i,j] in self.strategy.safeLocations:
                        if self.strategy.findPath(self.currentLocation, self.currentOrientation, destination, Orientation.RIGHT):
                            self.destination = destination
                            return
                    elif self.takeRisk:
                        self.strategy.addSafeLocation(destination[0],destination[1])
                        if self.strategy.findPath(self.currentLocation, self.currentOrientation, destination, Orientation.RIGHT):
                            self.destination = destination
                            self.takeRisk = 0
                            return
                        else:
                            self.strategy.removeSafeLocation(destination[0],destination[1])

    # Add safe locations around 
    def addSafeLocations(self):
        if self.currentLocation[0]-1>0:
            self.strategy.addSafeLocation(self.currentLocation[0]-1,self.currentLocation[1])

        if self.currentLocation[0]+1<5:
            self.strategy.addSafeLocation(self.currentLocation[0]+1,self.currentLocation[1])

        if self.currentLocation[1]-1>0:
            self.strategy.addSafeLocation(self.currentLocation[0],self.currentLocation[1]-1)

        if self.currentLocation[1]+1<5:
            self.strategy.addSafeLocation(self.currentLocation[0],self.currentLocation[1]+1)

    # Remove safe locations around 
    def removeSafeLocations(self):
        if self.currentLocation[1]-1>0:
            if [self.currentLocation[0],self.currentLocation[1]-1] not in self.explored:
                self.strategy.removeSafeLocation(self.currentLocation[0],self.currentLocation[1]-1)

        if self.currentLocation[1]+1<5:
            if [self.currentLocation[0],self.currentLocation[1]+1] not in self.explored:
                self.strategy.removeSafeLocation(self.currentLocation[0],self.currentLocation[1]+1)

        if self.currentLocation[0]-1>0:
            if [self.currentLocation[0]-1,self.currentLocation[1]] not in self.explored:
                self.strategy.removeSafeLocation(self.currentLocation[0]-1,self.currentLocation[1])

        if self.currentLocation[0]+1<5:
            if [self.currentLocation[0]+1,self.currentLocation[1]] not in self.explored:
                self.strategy.removeSafeLocation(self.currentLocation[0]+1,self.currentLocation[1])

    # Driver for adding safe locations
    def updateSafetyOfLocationsAround(self, percept):
        if percept['Stench'] == False and percept['Breeze'] == False:
            self.addSafeLocations()
        else:
            self.removeSafeLocations()
        if self.currentLocation not in self.explored:                
            self.explored.append(self.currentLocation[:])

    # Input percept is a dictionary [perceptName: boolean]
    def Process (self, percept):
        # If location is being explored for the first time
        if self.currentLocation not in self.explored:
            self.updateSafetyOfLocationsAround(percept)

        # If no gold yet
        if (not self.agentHasGold):
            if percept['Glitter']:
                # Make path to go back to location (1,1)
                self.updateSafetyOfLocationsAround(percept)
                self.goldLocation = self.currentLocation[:]
                self.actions = []
                self.actions.append(Action.GRAB)
                self.agentHasGold = True
                self.actions += self.strategy.findPath(self.currentLocation, self.currentOrientation, [1,1], Orientation.LEFT)
                self.actions.append(Action.CLIMB)

            elif not self.actions:
                # Action list is empty
                if self.currentLocation == self.destination:
                    self.strategy.addSafeLocation(self.currentLocation[0],self.currentLocation[1])
                    self.updateSafetyOfLocationsAround(percept)
                    
                    # Reached destination, where to go next
                    self.whereNext()
                    self.actions += self.strategy.findPath(self.currentLocation, self.currentOrientation, self.destination, Orientation.RIGHT)

        # Found nothing on action list (general check) 
        if not self.actions:
            # Action list is empty
            self.takeRisk = 1
            self.whereNext()
            self.actions += self.strategy.findPath(self.currentLocation, self.currentOrientation, self.destination, Orientation.RIGHT)

        if self.actions:   
        	action = self.actions.pop(0)
        else: 
        	action = random.randint(0,2)
        self.update_location_orientation(action)
        return action
    
    # Keeping track of location and orientation
    def update_location_orientation(self, action):
        if action == Action.GOFORWARD:
            if self.currentOrientation == Orientation.UP:
                self.currentLocation[1] += 1
            elif self.currentOrientation == Orientation.DOWN:
                self.currentLocation[1] -= 1
            elif self.currentOrientation == Orientation.RIGHT:
                self.currentLocation[0] += 1
            else:
                self.currentLocation[0] -= 1
            self.strategy.addSafeLocation(self.currentLocation[0],self.currentLocation[1])

        elif action == Action.TURNLEFT:
            self.decide_orientation(1) # add 1 to orientation on taking left
        elif action == Action.TURNRIGHT:
            self.decide_orientation(-1) # add -1 to orientation on taking right

    def decide_orientation (self, add_direction):
        self.currentOrientation += add_direction
        if self.currentOrientation > 3: # taking left from down will become right
            self.currentOrientation -= 4
        if self.currentOrientation < 0: # taking right from right will become down
            self.currentOrientation += 4

class Strategy:
    
    def __init__(self):
        self.toBeExplored = []
        self.alreadyExplored = []
        self.safeLocations = []

    def findPath (self, startLocation, startOrientation, goalLocation, goalOrientation):
        initial = State (startLocation, startOrientation, 0, None, Action.CLIMB)
        goal = State (goalLocation, goalOrientation, 0, None, Action.CLIMB)
        final = self.SearchPath (initial, goal)
        actions = []
        if (final):
            tmp = final
            while (tmp.previous):
                actions.insert(0, tmp.action)
                tmp = tmp.previous
        self.toBeExplored = []
        self.alreadyExplored = []
        return actions

    def SearchPath (self,initial, goal):
        self.toBeExplored = []
        self.alreadyExplored = []
        final = self.OptimizePath (initial, goal)
        sys.stdout.flush()
        return final

    def OptimizePath (self, initial, goal):
        initial.howFar = (abs (initial.location[0] - goal.location[0]) + abs (initial.location[1] - goal.location[1])) 
        initial.cost = initial.step + initial.howFar
        self.toBeExplored.append(initial)
        while (self.toBeExplored):
            state = self.toBeExplored.pop(0)
            if (state == goal):
                return state
            self.alreadyExplored.append (state)
            
            for action in [Action.GOFORWARD, Action.TURNLEFT, Action.TURNRIGHT]: # Try each action:
                next = self.GetNext(state, action)
                if (next):
                    next.howFar = (abs (next.location[0] - goal.location[0]) + abs (next.location[1] - goal.location[1])) 
                    next.cost = next.step + next.howFar
                    if (not self.Explored(next)):
                        self.AddToExplored(next)
                    else:
                        for idx,tmp in enumerate(self.toBeExplored):
                            if (tmp == next):
                                if (tmp.cost > next.cost):                                    
                                    self.toBeExplored[idx] = next # next state is better
                                
        return None # failure


    def GetNext (self, state, action):
        next = None
        if (action == Action.TURNLEFT):
            next = State (state.location, state.orientation, state.step + 1, state, Action.TURNLEFT)
            if (state.orientation == Orientation.UP):
                next.orientation = Orientation.LEFT
            if (state.orientation == Orientation.DOWN):
                next.orientation = Orientation.RIGHT
            if (state.orientation == Orientation.LEFT):
                next.orientation = Orientation.DOWN
            if (state.orientation == Orientation.RIGHT):
                next.orientation = Orientation.UP
        if (action == Action.TURNRIGHT):
            next = State (state.location, state.orientation, state.step + 1, state, Action.TURNRIGHT)
            if (state.orientation == Orientation.UP):
                next.orientation = Orientation.RIGHT
            if (state.orientation == Orientation.DOWN):
                next.orientation = Orientation.LEFT
            if (state.orientation == Orientation.LEFT):
                next.orientation = Orientation.UP
            if (state.orientation == Orientation.RIGHT):
                next.orientation = Orientation.DOWN
        if (action == Action.GOFORWARD):
            x = state.location[0]
            y = state.location[1]
            if (state.orientation == Orientation.UP):
                y += 1
            if (state.orientation == Orientation.DOWN):
                y -= 1
            if (state.orientation == Orientation.LEFT):
                x -= 1
            if (state.orientation == Orientation.RIGHT):
                x += 1
            if ([x,y] in self.safeLocations):
                next = State ([x,y], state.orientation, state.step + 1, state, Action.GOFORWARD)
        return next


    def addSafeLocation (self, x, y):
        if ([x,y] not in self.safeLocations):
            self.safeLocations.append([x,y])
    
    def removeSafeLocation(self, x, y):
        if ([x,y] in self.safeLocations):
            self.safeLocations.remove([x,y])

        
    # Return true if state on alreadyExplored or toBeExplored lists
    def Explored (self, state):
        if (state in self.alreadyExplored):
            return True
        if (state in self.toBeExplored):
            return True
        return False

    def AddToExplored (self, state):
        inserted = False
        for idx,tmp in enumerate(self.toBeExplored):
            if (tmp.cost >= state.cost):
                self.toBeExplored.insert(idx, state)
                inserted = True
                break
        if (not inserted):
            self.toBeExplored.append(state)



class State:
    
    def __init__(self, location, orientation, step, previous, action):
        self.location = location
        self.orientation = orientation
        self.step = step
        self.previous = previous
        self.action = action
        self.howFar = 0
        self.cost = 0
        
    def __eq__(self, other):
        if ((self.location == other.location) and (self.orientation == other.orientation)):
            return True
        else:
            return False


# Global agent
myAgent = 0

def PyAgent_Constructor ():
    print "PyAgent_Constructor"
    global myAgent
    myAgent = Agent()

def PyAgent_Destructor ():
    print "PyAgent_Destructor"

def PyAgent_Initialize ():
    print "PyAgent_Initialize"
    global myAgent
    myAgent.Initialize()

def PyAgent_Process (stench,breeze,glitter,bump,scream):
    global myAgent
    percept = {'Stench': bool(stench), 'Breeze': bool(breeze), 'Glitter': bool(glitter), 'Bump': bool(bump), 'Scream': bool(scream)}
    #print "PyAgent_Process: percept = " + str(percept)
    return myAgent.Process(percept)

def PyAgent_GameOver (score):
    print "PyAgent_GameOver: score = " + str(score)