# PyAgent.py

import Action
import Orientation
from itertools import combinations
import copy
import sys
    
class Agent:
    def __init__(self):
        
        self.agentHasGold = False
        self.agentHasArrow = True
        self.strategy = Strategy() # Will keep a track of pits and wumpus
        self.actionList = []
        self.current_location = [1,1]
        self.destination = [1,1]
        self.current_orientation = Orientation.RIGHT
        self.visited = [[1,1]]
        self.queries = {}
        self.goldLocation = []
        self.other = []
        self.lastAction = []
        self.locationFoundStench = []
        self.wumpusDead = False
        self.wumpusLocation = []
        self.known = []
        self.breeze = []
        self.strategy.addSafeLocation(1,1)        
        self.lastPerceptBreeze = False
    
    def Initialize(self):

        self.actionList = []
        self.Frontier = []
        self.wumpusDead = False
        self.agentHasArrow = True
        
        # Remember if it had climbed out because it couldn't find the gold the last time
        if self.current_location == [1,1] and self.agentHasGold == False and self.lastAction == Action.CLIMB:
        	self.actionList.append(Action.CLIMB)

        # Reinitialize that agent has gold
        self.agentHasGold = False

        if self.current_location != [1,1]:
            # If it died
            if self.lastPerceptBreeze:
                self.known.append(self.current_location[:]) # Update pit in current location
                currentlocation = self.current_location[:]
                self.strategy.removeSafeLocation(self.current_location[0],self.current_location[1])
            else:
            	# Killed by wumpus
                self.wumpusLocation.append(self.current_location[:]) # Update pit in current location
                self.strategy.removeSafeLocation(self.current_location[0],self.current_location[1])
            self.visited.append(self.current_location[:])
            self.current_location = [1,1]
            self.current_orientation = Orientation.RIGHT

        if self.goldLocation:
            # Gold found
            self.current_orientation = Orientation.RIGHT
            self.actionList = self.strategy.findPath(self.current_location, self.current_orientation, self.goldLocation, Orientation.RIGHT)

        elif self.wumpusLocation and self.wumpusLocation not in self.visited and self.wumpusLocation not in self.known:
            if str(self.wumpusLocation) in self.queries.keys():
                if self.queries[str(self.wumpusLocation)] < 0.5:
                    # Hunting for Wumpus
                    self.actionList=[]
                    if [self.wumpusLocation[0]-1,self.wumpusLocation[1]] in self.visited:
                        # Wumpus on the right
                        if self.current_location != [self.wumpusLocation[0]-1,self.wumpusLocation[1]]:
                            self.actionList += self.strategy.findPath(self.current_location, self.current_orientation, [self.wumpusLocation[0]-1,self.wumpusLocation[1]], Orientation.RIGHT)
                        self.actionList.append(Action.SHOOT)
                    elif [self.wumpusLocation[0],self.wumpusLocation[1]-1] in self.visited:
                        # Wumpus above
                        if self.current_location != [self.wumpusLocation[0],self.wumpusLocation[1]-1]:
                            self.actionList += self.strategy.findPath(self.current_location, self.current_orientation, [self.wumpusLocation[0],self.wumpusLocation[1]-1], Orientation.RIGHT)
                        self.actionList.append(Action.TURNLEFT)
                        self.actionList.append(Action.SHOOT)

        self.lastPerceptBreeze = False

    def getFrontier(self):
        
        self.Frontier = []

        locationsToCheck = self.visited+self.known

        for safeLocation_ in locationsToCheck:
            if safeLocation_[0]-1>0 and [safeLocation_[0]-1,safeLocation_[1]] not in self.visited and [safeLocation_[0]-1,safeLocation_[1]] not in self.Frontier:
                self.Frontier.append([safeLocation_[0]-1,safeLocation_[1]])

            if safeLocation_[0]+1<6 and [safeLocation_[0]+1,safeLocation_[1]] not in self.visited and [safeLocation_[0]+1,safeLocation_[1]] not in self.Frontier:
                self.Frontier.append([safeLocation_[0]+1,safeLocation_[1]])

            if safeLocation_[1]-1>0 and [safeLocation_[0],safeLocation_[1]-1] not in self.visited and [safeLocation_[0],safeLocation_[1]-1] not in self.Frontier:
                self.Frontier.append([safeLocation_[0],safeLocation_[1]-1])  

            if safeLocation_[1]+1<6 and [safeLocation_[0],safeLocation_[1]+1] not in self.visited and [safeLocation_[0],safeLocation_[1]+1] not in self.Frontier:
                self.Frontier.append([safeLocation_[0],safeLocation_[1]+1])


    # Check breeze consistency with frontier
    def breezeConsistency(self, pits):
        
        pits.extend(self.known) 

        for breeze_ in self.breeze:
            
            sum = 0

            if breeze_[0]-1>0 and [breeze_[0]-1,breeze_[1]] in pits:
                sum += 1

            if breeze_[0]+1<6 and [breeze_[0]+1,breeze_[1]] in pits:
                sum += 1

            if breeze_[1]-1>0 and [breeze_[0],breeze_[1]-1] in pits:
                sum += 1

            if breeze_[1]+1<6 and [breeze_[0],breeze_[1]+1] in pits:
                sum += 1

            if sum == 0:
                return 0

        return 1


    def calculateProbabilties(self):
        
        self.getFrontier()

        # 'Other' given frontier and known 
        self.other = []
        for i in range(1,6):
            for j in range(1,6):
                if [i,j] not in (self.Frontier+self.visited):
                    self.other.extend([[i,j]])

        self.queries = {}

        for query in self.Frontier:

            p_pit_true = 0.0
            p_pit_false = 0.0
            frontier_ = [loc_ for loc_ in self.Frontier if query!=loc_]

            Combinations = []
            
            for cLen in range(len(frontier_)+1):
                Combinations.append([c for c in combinations(frontier_,cLen)])
            
            # For each possible combo
            for c in Combinations:
                for combination in c:

                    numberOfTrue = 0
                    for _ in combination:
                        numberOfTrue+=1
                    
                    numberOfFalse = len(frontier_) - numberOfTrue

                    p = (0.2**numberOfTrue) * (0.8**numberOfFalse)

                    combination = list(combination)

                    if self.breezeConsistency([pit_ for pit_ in self.Frontier if pit_ in combination]):
                        p_pit_false += p

                    combination.append(query)

                    if self.breezeConsistency([pit_ for pit_ in self.Frontier if pit_ in combination]):
                        p_pit_true += p
            
            p_pit_true = p_pit_true*0.2
            p_pit_false = p_pit_false*0.8

            self.queries[str(query)]=p_pit_true/(p_pit_true+p_pit_false)

        self.print_probabilities()


    def print_probabilities(self):

        # print ("Visited----->",self.visited)
        # print ("frontier (includes query)-----> ", self.Frontier)
        # print ("breeze----->", self.breeze)
        # print ("others ----->", self.other)
        # print ("queries ----->", self.queries)

        print("P(pit):")
        for j in reversed(range(1,6)):
            print ("\n+------+------+------+------+------+")
            for i in range(1,6):
                print ("|"),
                if (str([i,j]) in self.queries.keys()):
                    print "%0.2f"%round(self.queries[str([i,j])],2),
                elif [i,j] in self.known:
                    print "1.00",
                elif [i,j] in self.other:
                    print "0.20", # 0.2
                else:
                    print "%0.2f"%0.00,
            print ("|"),
        print ("\n+------+------+------+------+------+")
        print ("\n")

    # Find safe unvisited location
    def whereNext(self):

        # Shoot if stench
        if self.locationFoundStench and self.agentHasArrow == True and self.wumpusLocation not in self.visited:
            # Find unsafe location around
            if self.locationFoundStench[0]!=4:
                # Go to stench
                if self.current_location != self.locationFoundStench:
                    # Kill wumpus if location != current location
                    self.actionList += self.strategy.findPath(self.current_location, self.current_orientation, self.locationFoundStench, Orientation.RIGHT)
                if self.current_orientation == Orientation.UP:
                    self.actionList.append(Action.TURNRIGHT)
                self.actionList.append(Action.SHOOT)
                
            elif self.locationFoundStench[0]==4:
                # Wumpus above. Go to stench
                if self.current_location != self.locationFoundStench:
                    # Kill wumpus if location != current location
                    self.actionList += self.strategy.findPath(self.current_location, self.current_orientation, self.locationFoundStench, Orientation.RIGHT)
                if self.current_orientation == Orientation.RIGHT:
                    self.actionList.append(Action.TURNLEFT)
                elif self.current_orientation == Orientation.LEFT:
                    self.actionList.append(Action.TURNRIGHT)
                self.actionList.append(Action.SHOOT)
                
        else:
            if self.queries.keys():
                # Go to lowest P value
                minKey = min(self.queries, key=self.queries.get)

                while self.queries[minKey] < 0.5:

                    self.queries.pop(minKey, None)
                    key = minKey[1:-1].split(",") 
                    destination = [int(key[0]),int(key[1])]

                    # Add destination as a safe location
                    if destination!=self.wumpusLocation:
                        self.strategy.addSafeLocation(destination[0],destination[1])
                    
                    # Check for Path
                    if self.strategy.findPath(self.current_location, self.current_orientation, destination, Orientation.RIGHT):
                        self.destination = destination
                        return
                    else:
                        self.strategy.removeSafeLocation(destination[0],destination[1])

                        self.queries.pop(minKey, None)

                        if self.queries.keys():
                            minKey = min(self.queries, key=self.queries.get)
                        else:
                            break

            # No place to go except back
            self.destination = [1,1]
            return

    def addSafeLocations(self):
        if self.current_location[0]-1>0:
            self.strategy.addSafeLocation(self.current_location[0]-1,self.current_location[1])

        if self.current_location[0]+1<6:
            self.strategy.addSafeLocation(self.current_location[0]+1,self.current_location[1])

        if self.current_location[1]-1>0:
            self.strategy.addSafeLocation(self.current_location[0],self.current_location[1]-1)

        if self.current_location[1]+1<6:
            self.strategy.addSafeLocation(self.current_location[0],self.current_location[1]+1)

    def removeSafeLocations(self):
        if self.current_location[1]-1>0:
            if [self.current_location[0],self.current_location[1]-1] not in self.visited:
                self.strategy.removeSafeLocation(self.current_location[0],self.current_location[1]-1)

        if self.current_location[1]+1<6:
            if [self.current_location[0],self.current_location[1]+1] not in self.visited:
                self.strategy.removeSafeLocation(self.current_location[0],self.current_location[1]+1)

        if self.current_location[0]-1>0:
            if [self.current_location[0]-1,self.current_location[1]] not in self.visited:
                self.strategy.removeSafeLocation(self.current_location[0]-1,self.current_location[1])

        if self.current_location[0]+1<6:
            if [self.current_location[0]+1,self.current_location[1]] not in self.visited:
                self.strategy.removeSafeLocation(self.current_location[0]+1,self.current_location[1])

    def updateSafetyOfLocationsAround(self, percept):

        # No stench or breeze || just breeze if wumpus dead
        if (percept['Stench'] == False and percept['Breeze'] == False) or (self.wumpusDead and percept['Breeze'] == False):
            self.addSafeLocations()
        elif self.wumpusLocation and percept['Stench'] and percept['Breeze'] == False:
            # wumpus location known and no breeze
            self.addSafeLocations()

            if self.wumpusDead == False:
                # wumpus location known
                self.strategy.removeSafeLocation(self.wumpusLocation[0],self.wumpusLocation[1])

        else:
            self.removeSafeLocations()

        if self.current_location not in self.visited:                
            self.visited.append(self.current_location[:])

    def Process (self, percept):

        FlagCheckProb = False

        # First visit to loc
        if self.current_location not in self.visited:
            self.updateSafetyOfLocationsAround(percept)
            if percept['Breeze']:
                self.breeze.append(self.current_location[:])
                if not self.agentHasGold:
                    self.actionList = []
        elif self.current_location == [1,1] and percept['Breeze'] and [1,1] not in self.breeze:
            self.breeze.append([1,1])

        # Post mortem -> Pit of Wumpus
        if percept['Breeze'] == True:
            self.lastPerceptBreeze = True

        if (not self.agentHasGold):
            if percept['Glitter']:
                # Go back to 1,1
                self.updateSafetyOfLocationsAround(percept)
                self.goldLocation = self.current_location[:]
                self.actionList = []
                self.actionList.append(Action.GRAB)
                self.agentHasGold = True
                self.actionList += self.strategy.findPath(self.current_location, self.current_orientation, [1,1], Orientation.LEFT)
                self.actionList.append(Action.CLIMB)

        if FlagCheckProb == False:
            ##### Mandatory calculation before taking a step #####
            self.calculateProbabilties()
            if str(self.destination) in self.queries.keys():
                if self.queries[str(self.destination)]>0.5:
                    self.actionList = []
            FlagCheckProb = True

        ##### Found nothing on action list (general check) #####
        if not self.actionList:

            self.whereNext()

            # No safe loc, go back and climb out
            if not self.actionList:
                self.actionList += self.strategy.findPath(self.current_location, self.current_orientation, self.destination, Orientation.RIGHT)
                if self.destination == [1,1]:
                    self.actionList.append(Action.CLIMB)

        action = self.actionList.pop(0)

        # Already has gold
        forward_location = self.current_location[:]
        if action == Action.GOFORWARD and self.wumpusDead==False and self.agentHasArrow:
            if self.current_orientation == Orientation.RIGHT:
                forward_location[0] += 1
            elif self.current_orientation == Orientation.LEFT:
                forward_location[0] -= 1
            elif self.current_orientation == Orientation.UP:
                forward_location[1] += 1
            elif self.current_orientation == Orientation.DOWN:
                forward_location[1] -= 1

            if forward_location == self.wumpusLocation:
                if Action.SHOOT in self.actionList:
                    self.actionList.remove(Action.SHOOT)
                self.actionList = list([Action.GOFORWARD]) + self.actionList
                action = Action.SHOOT

        self.update_location_orientation(action)

        self.lastAction = action

        if action == Action.SHOOT:
            self.agentHasArrow = False

        return action
    
    def update_location_orientation(self, action):
        if action == Action.GOFORWARD:
            if self.current_orientation == Orientation.UP:
                self.current_location[1] += 1
            elif self.current_orientation == Orientation.DOWN:
                self.current_location[1] -= 1
            elif self.current_orientation == Orientation.RIGHT:
                self.current_location[0] += 1
            else:
                self.current_location[0] -= 1
            self.strategy.addSafeLocation(self.current_location[0],self.current_location[1])

        elif action == Action.TURNLEFT:
            self.decide_orientation(1) 
        elif action == Action.TURNRIGHT:
            self.decide_orientation(-1) 

    def decide_orientation (self, add_direction):
        self.current_orientation += add_direction
        if self.current_orientation > 3: 
            self.current_orientation -= 4
        if self.current_orientation < 0: 
            self.current_orientation += 4

    def GameOver(self, score):
        pass



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
    global myAgent
    myAgent = Agent()

def PyAgent_Destructor ():
    global myAgent
    # nothing to do here

def PyAgent_Initialize ():
    global myAgent
    myAgent.Initialize()

def PyAgent_Process (stench,breeze,glitter,bump,scream):

    print ("\n#########################\n")

    global myAgent
    percept = {'Stench': bool(stench), 'Breeze': bool(breeze), 'Glitter': bool(glitter), 'Bump': bool(bump), 'Scream': bool(scream)}
    
    #### If the last action was shoot and it missed the wumpus then the wumpus is above (UP) the agent
    if myAgent.lastAction == Action.SHOOT and percept['Scream'] == False and myAgent.wumpusDead == False:
        myAgent.wumpusLocation = [myAgent.current_location[:][0], myAgent.current_location[:][1]+1]
    elif percept['Scream']:
        #### If the wumpus died then update flag that it's dead #####
        myAgent.wumpusDead = True

        #### Also update the Wumpus's location #####
        forward_location = myAgent.current_location[:]
        if myAgent.current_orientation == Orientation.RIGHT:
                forward_location[0] += 1
        elif myAgent.current_orientation == Orientation.LEFT:
            forward_location[0] -= 1
        elif myAgent.current_orientation == Orientation.UP:
            forward_location[1] += 1
        elif myAgent.current_orientation == Orientation.DOWN:
            forward_location[1] -= 1

        ##### Decide whether wumpus location is safe or not based on breeze else if breeze is there then check prob. of pit #####
        myAgent.wumpusLocation = forward_location
        if percept['Breeze']==False:
            myAgent.strategy.addSafeLocation(myAgent.wumpusLocation[0],myAgent.wumpusLocation[1])
        elif str(myAgent.wumpusLocation) in myAgent.queries:
            if myAgent.queries[str(myAgent.wumpusLocation)]:
                myAgent.strategy.addSafeLocation(myAgent.wumpusLocation[0],myAgent.wumpusLocation[1])            

    ##### Location where wumpus might be #####
    ##### Will be used to kill wumpus and create safer places to move around #####
    if percept['Stench']:
        myAgent.locationFoundStench = myAgent.current_location[:]

    ##### Uncomment to stop at each iteration #####
    # raw_input("Press the <ENTER> key to continue...")
    return myAgent.Process(percept)

def PyAgent_GameOver (score):
    global myAgent
    myAgent.GameOver(score)
