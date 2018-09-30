#Implement a Schelling Housing Segregation Model

import tkinter as tk #Tkinter in python2 or before. 
import numpy as np
import random

'''
Explanation: 

Inputs:     
    grid - The 'City' we are evaluating. It is an N by N grid (list of lists) 
    where each House (i,j coord) is either a Red Person, Open, or a Blue person
    (strings R, O, B).      
    
    R - The radius of the neighborhood: home (i, j) is in the
        neighborhood of home (k,l) if |k-i| + |l-j| <= R.

    threshold - The minimum acceptable threshold for ratio of neighbor
    value to the total number of homes in his neighborhood.

    max_steps - The maximum number of passes to make over the
    neighborhood during a simulation.  
    
Method:     
    A person is satisfied if there satisfaction score is greater or equal to the 
    threshold; satisfaction score is just the average number of similar people
    in the neighborhood (S = Same + .5 * Open spaces). If they are unsatisfied, 
    a person relocates to the first open house. This continues till either 
    everyone is satisfied, or we've hit the maximum number of steps. 

    Only people within the city are counted towards satification - therefore
    people who's neighborhood overlaps with the edge of the city have fewer
    neighbors.
    
Limitations:
    This approach assumes an N by N grid. Normal cities don't have these 
    boundaries. This could be fixed by generalizing our 'edge' population.
    
    We are assuming that every person in the neighborhood counts equally; 
    perhaps it would be better to assume more distant people count less.
    
    Naturally, there are more than 2 types of people. We could define a 
    gradient of color rather than binary options.  
    
    Finally, other non-racial effects come into play in the real world, 
    proximity to job, the notion that not all houses are equally priced, etc.
'''


class Simulation:
        
    def __init__(self, root, grid, R, threshold, max_num_steps):

        x = len(grid)
        y = len(grid[0]) #Assumes only square cities. 

        self.root = root
        self.size_x = x
        self.size_y = y
        
        # Simulation parameters
        self.grid = grid
        self.radius = R
        self.threshold = threshold
        self.max_steps = max_num_steps
        
        self.relocs = 1  
        self.count = 0 
        #^Setup a list of open locations from a function to find them
        self.locations_open = self.locs_open()

        # Interface parameters
        self.sq_size    = 50  #Each place = 50 pixels wide - adjust this later 
        #it should depend on the size of the grid
        self.win_x      = self.sq_size*x #Find the window size - columns by rows
        self.win_y      = self.sq_size*y

    def setup_canvas(self):
        """
        Designate simulation GUI environment
        """
        self.c = tk.Canvas(self.root, width=self.win_x, height=self.win_y)
        self.c.pack()
        
    def make_sat_square(self, i, j):
        """
        Makes a square colored depending on the location input. Don't color
        squares that aren't 
        """
        color = 'black'
        if self.grid[i][j] == 'O':
            color = 'snow'
        elif self.grid[i][j] == 'B':
            color = 'blue'
        elif self.grid[i][j] == 'R':
            color = 'red'
        else: 
            print('Grid location not O, B, or R?')
        

        # Apply that color value to a rectangle at the proper location
        s = self.sq_size
        bounds = [s*j, s*i, s*(j+1), s*(i+1)]
        self.c.create_rectangle(*bounds, fill=color, outline='#101010')
        #Slight adjustments - prev line = sq, then returned sq. Don't think nec.

    def make_unsat_square(self, i, j):
        """
        Makes a square colored depending on the location input. Color's
        unsatisfied squares.
        """
        color = 'black'
        if self.grid[i][j] == 'B':
            color = 'dodger blue'
        elif self.grid[i][j] == 'R':
            color = 'light coral'
        else: 
            print('Grid unsat location not B, or R?')
            color = 'black'    

        # Apply that color value to a rectangle at the proper location
        s = self.sq_size
        bounds = [s*j, s*i, s*(j+1), s*(i+1)]
        self.c.create_rectangle(*bounds, fill=color, outline='#101010')                
        
    ###################
    # Simulation Code #   
    ###################
    
    def locs_open(self):        
        '''
        Find the open locations within my grid. 
        
        Returns: list of touples - [(i,j),(i1,j1)...]
        ''' 
           
        locations_open = []
        for i in range(len(self.grid)):
            for j in range(len(self.grid)): 
                if self.grid[i][j] == 'O':
                    locations_open.append((i,j))
                    
        return locations_open
    
    def count_neighbors(self, location):
            
        '''
        Find the number of neighbors with the same values as oneself,
        the number of open neighbors, and the number of neighbors
        with different values from oneself.
    
        Return: <int, int, int>, number of neighbors with same value as oneself,
            number of open neighbors, number of different neighbors
        '''
        
        i, j = location
        own_value = self.grid[i][j]
        same_neighbors = 0
        open_neighbors = 0
        dif_neighbors = 0
        for k in range(i - self.radius, i + self.radius + 1):
            for l in range(j - self.radius, j + self.radius + 1):
                #ensure you're in the neighborhood, and not out of the city.
                if 0 <= (abs(i - k) + abs(j - l))\
                and (abs(i - k) + abs(j - l)) <= self.radius\
                and l >= 0 and l < len(self.grid)\
                and k >= 0 and k < len(self.grid):
                    value = self.grid[k][l]
                    if value == own_value:
                        same_neighbors += 1
                    elif value == 'O':
                        open_neighbors += 1
                    elif value != own_value:
                        dif_neighbors += 1

        return same_neighbors, open_neighbors, dif_neighbors

    def is_satisfied(self, location):
        '''
        Is the homeowner at the specified location satisfied?
    
        Returns: True, if the location's neighbor score is at or above the threshold
        '''
            
        # Added an assertion to check that the location does
        # not contain an open (unoccupied) home - testing phase only.  
        satisfied = False
        s, o, d = self.count_neighbors(location)
        denom = float(s + o + d)
        if (s + 0.5 * o) / denom >= self.threshold:
            satisfied = True
        return satisfied    
        
    def unsatisfied_list(self):
        '''
        Runs through the given grid and returns a list of locations with 
        unsatisfied homeowners, and open locations.
    
        Returns: list of tuples - unsatisfied locations,
        '''
    
        locations_unsat = []
        #Run through each location in the grid
        for i in range(len(self.grid)):
            for j in range(len(self.grid)): 
                #Return a list of unsatisfiied homeowners
                if self.grid[i][j] != 'O' and not self.is_satisfied((i,j)):
                    locations_unsat.append((i,j))
        
        return locations_unsat  
        
    def relocate_owner(self):
        '''
        Goes through one step of the simulation and produces number of relocations that
        occur in one step.
    
        Returns: int, 
        '''
    
        locations_unsat = self.unsatisfied_list()
        relocations = 0
    
        for place in locations_unsat:
            i,j = place
            #For an open location, set the value of the location to the unsatisfied person's color.
            #then check if that location is satisfied. If it is, set the original position to 'O'
            #and put it at the front of the open list. If not, reset it to 'O', and try the next.  
            #There is some chance the movement of previous unsatisfied people within a step satisfied 
            #the current unsatisfied person - so we must recheck that they're unsatisfied.
            if not self.is_satisfied(place): 
                for loc in self.locations_open:
                    m,n = loc
                    #Set the open location to the color of the unsatisfied person you're testing.
                    #Set the old location equal to open.
                    self.grid[m][n] = self.grid[i][j]
                    self.grid[i][j] = "O"
                    #If they're satisfied, they relocate.
                    #The old location is set to open and put at the start of the new list.
                    #The new location is no longer open.
                    if self.is_satisfied(loc):
                        relocations += 1
                        self.locations_open.insert(0, (i,j))
                        self.locations_open.remove(loc)
                        break
                    #If they're not satisfied, flip the position back to its original value 
                    #and return the trial postion back to open
                    else:
                        self.grid[i][j] = self.grid[m][n]
                        self.grid[m][n] = 'O'  
                        
        return relocations            
        
    def animate(self):
        '''
        Repeats steps of the simulation until either we reach the max number of steps
        or there are no more relocations
    
        Return: int, list of lists - number of steps taken in the simulation, final 
        city
        '''
        
        if(self.count < self.max_steps and self.relocs != 0):  
            #Color the Grid appropriately 
            unsat_locs = self.unsatisfied_list()
            for i in range(self.size_x):
                for j in range(self.size_y):
                    self.make_sat_square(i, j)
                    if (i,j) in unsat_locs:
                        self.make_unsat_square(i, j)
            
            #Do a step of the simulation
            self.relocs = self.relocate_owner()

            #Keep track of the steps
            self.count += 1
            self.root.after(2500, self.animate)
        
        else:
            print('Simulation Complete')
            if self.count >= self.max_steps:
                print('The simulation hit the maximum number of steps.')
            if self.relocs == 0:
                print('There were no successful relocations, so the board is complete.')
            
    def do_simulation(self):
        self.setup_canvas()        
        self.animate()

def city_generator(size):
    #Size is the x & y length of the grid. 
    city = []
    for i in range(size):
        row = []
        for j in range(size):
            val = random.random()
            #For now, just assume and R & B are .4 each.
            house = to_house(val, .4, .4)
            row.append(house)
        city.append(row)
    return city

def to_house(value, p1, p2):
    '''
    Value: float you're converting.
    p1: float for probability of getting a red person.
    p2: float for probability of getting a blue person.
    '''
    if value < p1:
        return 'R'
    elif value > (1 - p2):
        return 'B'
    else:
        return 'O'

        
root = tk.Tk()
#grid1 = [['R', 'R', 'O', 'R', 'R'],['O', 'B', 'B', 'B', 'B'],['R', 'R', 'R', 'R', 'R'],['B', 'B', 'B', 'O', 'B'],['R', 'O', 'R', 'R', 'O']]
# ^ Useful demonstration grid w/ R = 1, threshold = .51.
city = city_generator(8)
Sim = Simulation(root, city, 3, .51, 100)
Sim.do_simulation()
tk.mainloop()


