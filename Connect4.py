#Implement

import tkinter as tk #tkinter as of python3, Tkinter in python2.
import numpy as np

class connect_four:

    def __init__(self, root, game_type):
        #game type is person v person or person v computer
        self.root = root
        self.sq_size = 50
        self.size_x = 7
        self.size_y = 6
        self.player = 1 #Keeps track of current player
        self.player_val = 0 #Keeps track of which player is the human.
        self.frame = tk.Frame(root)
        self.win_x = self.size_x * self.sq_size
        self.win_y = self.size_y * self.sq_size
        self.game_type = game_type
        self.grid = np.zeros((self.size_x, self.size_y), dtype = int)
        self.k = 0 #Used for keeping track of the current or previous move
        self.l = 0
        self.m = 0 #Used for keeping track of a simulated move
        self.n = 0
        self.done = False #Used for testing if game ends.
        
    def setup_canvas(self):
        """
        Designate simulation GUI environment. Sets up keypress interface.
        Sets up buttons.
        """
        button = tk.Button(self.root, 
                   text="Quit", 
                   fg="red",
                   command=quit)
        button2 = tk.Button(self.root, 
                   text="Reset", 
                   fg="red",
                   command=self.reset)
        button3 = tk.Button(self.root, 
                   text="Undo Last Move", 
                   fg="red",
                   command=self.undo)
        button.pack()#side = "top")
        button2.pack()#side = "top")
        button3.pack()#side = "top")
        self.c = tk.Canvas(self.root, width=self.win_x, height=self.win_y)
        self.c.focus_set()
        self.c.bind('<Key>', self.keypress)
        self.c.pack(side = 'bottom')    
        
    def paint_square(self, i, j):
        """
        Makes a square colored depending on the location input. 
        """
        color = 'black'
        if self.grid[i][j] == 0:
            color = 'snow'
        elif self.grid[i][j] == 1:
            color = 'red'
        elif self.grid[i][j] == 2:
            color = 'blue'
        else: 
            print('Grid location not open, red, or blue?')
        if i > 6:
            print(i, j)
            print(color)
        #Apply that color value to a rectangle at the proper location
        s = self.sq_size
        bounds = [s*i, s*j, s*(i+1), s*(j+1)]
        self.c.create_rectangle(*bounds, fill=color, outline='#101010')

    #################
    ### INTERFACE ###
    #################

    def keypress(self, event):
        '''
        Sets the keys to paint the square. Then swap players.
        '''
        i = event.char

        #If entering player 1 or 2 - you can't change this past the start of the game.
        if self.player_val == 0:
            if i == "a" or i == "A":
                print("Player 1 input")
                self.player_val = 1
            elif i == "b" or i == "B":
                print("Player 2 input")
                self.player_val = 2
                self.calc_move() #here so that the game starts
            else:
                print("You must first choose your player by typing A or B.")

        #If entering column for chip.
        if i.isdigit() and not self.done:
            i = int(i)
            i = i - 1 #Assuming humans are not indexing from 0. 
            if i not in range(7):
                print("Columns are only 1 - 7")
            elif self.player == self.player_val and i in range(7): 
                j = self.find_bottom_row(self.grid, i)
                if j < 0:
                    print("That column is already full")
                else:
                    self.k = i
                    self.l = j
                    self.grid[i][j] = self.player
                    self.paint_square(self.k, self.l)
                    pos = (i, j)
                    player_flex = self.calc_flexibility(pos, \
                        self.player, self.grid)
                    if player_flex >= 600:
                        self.done = True
                        print("The humans have done it! \
                            We've beaten those durn machines!")
                    else:
                        self.player_swap()
                        if self.player != self.player_val:
                            self.calc_move()


    ###################
    # Simulation Code #   
    ###################

    def is_valid(self, i, j):
        #Unused - old
        if (i < self.size_x) and (i >= 0) and \
           (j < self.size_y) and (j >= 0):
            return True
        else:
            return False

    def calc_move(self):
        moves = []
        opens = self.find_opens(self.grid)

        for position in opens:           
            i, j = position
            grid_pointer = self.grid
            temp_grid = grid_pointer.copy()
            temp_grid[i][j] = self.player
            flex = self.calc_flexibility(position, self.player, temp_grid)    

            if flex >= 600: 
                #Do move b.c. this means the move wins.
                self.grid[i][j] = self.player
                self.paint_square(i, j)
                print("Computer player wins!")
                self.player_swap()
                self.m = i
                self.n = j
                self.done = True
                break
            
            else:
                opponent_flexs = []
                opens2 = self.find_opens(temp_grid)     
                for position2 in opens2:
                    i1, j1 = position2
                    temp_grid2 = temp_grid.copy()
                    temp_grid2[i1][j1] = self.other_player()
                    opp_flex = self.calc_flexibility(position2, \
                        self.other_player(), temp_grid2)
                    opponent_flexs.append(opp_flex)
                #The case where the entire board is almost filled up.
                if len(opponent_flexs) != 0:
                    neg_flex = max(opponent_flexs)
                else:
                    neg_flex = 0

                neg_flex = -2 * neg_flex
                total_flex = neg_flex + flex
                tup = (position, total_flex)
                moves.append(tup)

        if len(moves) != 0 and (not self.done): #If = 0 then calc move should have found a winning move.
            move = max(moves, key=lambda item:item[1])[0] #DETERMINISTIC VERSION (Ok, but boring atm)
            #move = self.prob_move(moves) #PROBABALISTIC VERSION (Not very good atm)
            i, j = move
            self.m = i
            self.n = j
            self.grid[i][j] = self.player
            self.paint_square(i, j)
            self.player_swap()
                  
    def prob_move(self, moves):
        '''
        Takes an input of the type moves outputs, that is a list of tuples, 
        with each tuple being a position tuple and a flex score, 
        turns it into a semi-skewed probability distribution, and finally
        picks a move.
        '''
        pscores = []

        #Step A: Make sure all neg flex's - most likely.
        if all(item[1] <= 0 for item in moves):
            #random choice can't accept a list of tuples, so use indexs.
            indexs = range(0, len(moves))
            for move in moves:
                flex = round(move[1], 1)
                flex = 1.0/flex
                f2 = round(flex**3, 12) #Skew the distribution more. 
                f2 = abs(f2)
                pscores.append(f2)
            print("Negs case SUM", sum(pscores))
            summ = sum(pscores) #Trying to figure out why nan issues
            pscores = np.array(pscores)/summ
            print("Negs case", pscores)
            choice_index = np.random.choice(indexs, p = pscores)
            move = moves[choice_index]
            move = move[0]
            return move

        #If any positives: 
        #Why: for f1 = 2 * f2, both positive, f1 is twice as good as f2.
        #for f1 = 2 * f2, both neg, f1 is twice as bad as f2. 
        #But if different signs, no valid comparison (aside from pos = good)
        else:
            positives = []
            for move in moves:
                if move[1] > 0:
                    positives.append(move)
            indexs = range(0, len(positives))
            for pos_move in positives:
                flex = move[1]
                f2 = round(flex**2, 2)
                pscores.append(f2)
            pscores = np.array(pscores)/sum(pscores)
            print("One+ Pos", pscores)
            choice_index = np.random.choice(indexs, p = pscores)
            move = positives[choice_index]
            move = move[0]
            return move


    def other_player(self):
        if self.player == 1:
            return 2
        elif self.player == 2:
            return 1
        else:
            print("Somehow player is not 1 or 2 when using Other Player func")

    def to_score(self, count):
        #Converts a number in a row to a flexibility score.
        if count < 1:
            return 2
        elif count == 1:
            return 8
        elif count == 2:
            return 32
        #Have 4 in a row vastly overweight.
        elif count >= 3:
            return 1000

    def pos_score_mod(self, score, pos):
        #More flexible if position is near the center - use mults for this.
        i, j = pos
        if i == 3:
            mult1 = 4
        elif i == 2 or i == 4:
            mult1 = 2
        elif i == 1 or i == 5:
            mult1 = 1
        else:
            mult1 = .5

        if j == 2:
            mult2 = 3
        elif j == 1 or j == 3:
            mult2 = 1.5
        elif j == 0:
            mult2 = 1
        else:
            mult2 = 0.5

        return score * mult1 * mult2


    def calc_flexibility(self, pos, cur_player, board):

        '''
        Every move has a corresponding flexibility score. We calculate this
        from the number of similar player chips that are in a row,
        either horizontally, vertically, or diagonally and sum each individual
        score. Note number in a row is converted to a flexibility score, they
        are not identical - 3 in a row is weighted more than 1 in a row.

        pos - tuple contain the grid cordinates you want to place
        cur_player - the value of the player (yours or opponent/ 1, 2) 
            whos move you'll be calculating
        board - the board you'll be calculating on - an array.

        returns a float which represents the flexibility of the input move.
        '''

        i = pos[0]
        j = pos[1]
        vert_mat = range(6)
        hori_mat = range(7)
        flex = 0
        #Verticle
        vert_count = 0
        for h in range(1,4):
            if (j + h) in vert_mat: #Plus signs b.c. my matrix fills from the top down
                if cur_player == board[i][j + h]:
                    vert_count += 1
                else:
                    break
        #print("Vert Count: ", vert_count)
        flex += self.to_score(vert_count)

        #Horizontal
        hori_count = 0
        #Need two separate for loops so you don't break counting backwards 
        #if you run into a dif color going forwards.
        for h in range(1,7):
            if (i + h) in hori_mat:
                if cur_player == board[i + h][j]:
                    hori_count += 1
                else:
                    break
        for h in range(1,7):
            if (i - h) in hori_mat:
                if cur_player == board[i - h][j]:
                    hori_count += 1
                else:
                    break
        #print("Hori Count: ", hori_count)
        flex += self.to_score(hori_count)

        #Diagonal1
        diag1_count = 0
        for h in range(1,6):
            if ((i + h) in hori_mat) and ((j + h) in vert_mat):
                if cur_player == board[i + h][j + h]:
                    diag1_count += 1
                else:
                    break

        for h in range(1,6):
            if ((i - h) in hori_mat) and ((j - h) in vert_mat):
                if cur_player == board[i - h][j - h]:
                    diag1_count += 1
                else:
                    break                    

        #print("Diag1 Count: ", diag1_count)
        flex += self.to_score(diag1_count)

        #Diagonal2
        diag2_count = 0
        for h in range(1,6):
            if ((i + h) in hori_mat) and ((j - h) in vert_mat):
                if cur_player == board[i + h][j - h]:
                    diag2_count += 1
                else:
                    break

        for h in range(1,6):
            if ((i - h) in hori_mat) and ((j + h) in vert_mat):
                if cur_player == board[i - h][j + h]:
                    diag2_count += 1
                else:
                    break                    

        #print("Diag2 Count: ", diag2_count)
        flex += self.to_score(diag2_count)

        flex = self.pos_score_mod(flex, pos)

        #print(flex)
        return flex

    def player_swap(self):
        if self.player == 1:
            self.player = 2
        elif self.player == 2:
            self.player = 1
        else:
            print("Somehow player is not 1 or 2?")

    def find_bottom_row(self, grid, column):
        #For a given column, find the min row thats empty.
        max_j = -1
        for j in range(self.size_y):
            if grid[column][j] == 0:
                if j > max_j:
                    max_j = j
        return max_j

    def find_opens(self, grid):
        #Return a list of bottom spots that are open.
        opens = []
        for i in range(self.size_x):
            max_j = self.find_bottom_row(grid, i)
            if max_j != -1:
                loc = (i, max_j)
                opens.append(loc)
        return opens

    def color_grid(self):
        #Go through each loc & color it.
        for i in range(self.size_x):
            for j in range(self.size_y):
                self.paint_square(i, j)

    def reset(self):
        #Resets the board to all white. 
        self.grid = np.zeros((self.size_x, self.size_y), dtype = int)
        self.color_grid()
        self.player = 1
        self.player_val = 0
        self.done = False
        print("If you would like to play first, enter A. If you would like to play second, enter B.")
        print()
        print("Use number keys 1 - 7 to enter the row you would like to deposit your chip on.")   

    def undo(self):
        self.done = False
        #Check if win - if won, need to scrap message? 
        if self.grid[self.k][self.l] != 0: #Need to ensure the right player is kept if pressed multiple times.
            self.grid[self.k][self.l] = 0
            self.grid[self.m][self.n] = 0
            self.paint_square(self.k, self.l)
            self.paint_square(self.m, self.n)

    def test_game(self):
        #Setup & run game.
        self.setup_canvas()
        self.color_grid()

print("If you would like to play first, enter A. If you would like to play second, enter B.")
print()
print("Use number keys 1 - 7 to enter the row you would like to deposit your chip on.")                
root = tk.Tk()
Sim = connect_four(root, 1)
Sim.test_game()
tk.mainloop()
            
