from random import randint
from BoardClasses import Move
from BoardClasses import Board

import time
from math import sqrt, log, sin

#The following part should be completed by students.
#Students can modify anything except the class name and existing functions and variables.

class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.sim_board = Board(col, row, p)
        self.sim_board.initialize_game()
        self.opponent = {1:2,2:1}
        self.color = 2
        self.turn_count = 0
        self.extra_time = 0

        self.c_value = sqrt(2) #work on c value afterwards poor-ai
        self.root = TreeNode(turn = 0)
        self.root._games += 1

    def get_move(self,move):
        # print("my first move:", move) #If prints -1, then len(move) == 0
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
            self.sim_board.make_move(move, self.opponent[self.color])
            
            if self.root._turn == 0:
                self.root._turn = self.opponent[self.color]
                self.root._move = move

            if not self.root._children:
                self.expansion(self.root)
            for child in self.root._children:
                # if child.move() == move:
                # print("first string:", str(child.move()), "== second string:", str(move))
                if str(child.move()) == str(move):
                    self.root = child
                    # print("new for loop in here")
                    break
        else:
            self.color = 1
        
        if self.root._turn == 0:
            self.root._turn = self.opponent[self.color]
            self.root._move = move
        #We can implement a time limit (5 - 10 seconds)

        #for simulation
        #set a variable to equal avg depth of explored finished games and limit simulation so
        #it doesn't go past the avg depth
        #OUR CODE

        whileFlag = True
        if len(self.root._children) == 1:
            whileFlag = False
            if self.turn_count < 41:
                self.extra_time += self.sin_time()

        start_time = time.time()
        end_time = time.time()
        time_taken = (self.sin_time() + self.extra_time) if self.turn_count <= 36 else 1
        while whileFlag and ((end_time - start_time) < time_taken): #300 secs / 40 moves = 7.5 secs per move, so i think 6 is safe
            # print(end_time)
            leaf_node = self.selection(self.root)
            # print("my leaf node:", leaf_node)
            term_node, winner = self.simulation(leaf_node)
            self.backtracking(term_node, winner)
            end_time = time.time()
        
        if whileFlag:
            self.extra_time = 0

        # total_games = 0
        # for i in self.root.children():
        #     print(round(i._wins, 3), "/", round(i._games, 3), "and", round(log(i._parent._games), 3), "/", round(i._games, 3), "and", round(i.UCT(self.c_value), 3))
        #     total_games += i._games
        
        # print("total games:", total_games)
        
        self.root = self.root.pick_best_child()

        # temp = str(self.root._wins) + "/" + str(self.root._games)
        # print("wanted move:", self.root, temp)
        
        self.board.make_move(self.root._move,self.color)
        self.sim_board.make_move(self.root._move, self.color)

        self.turn_count += 1
        # if whileFlag:
        #     print("time taken:", time_taken)
        # else:
        #     print("only one choice")
        return self.root._move

    def sin_time(self):
        return 4*sin(self.turn_count / 12.732) + 4.5

    def evaluation(self):
        pass

    '''pick child with highest UCT'''
    def selection(self, node: 'TreeNode'):
        current = node
        while current._children:
            current = current.pick_child(self.c_value)
            # print("current in selection:", current)
            # print("my move:", current.move(), "turn:", current.turn())
            # self.sim_board.show_board()
            self.sim_board.make_move(current.move(), current.turn())
            # self.sim_board.show_board()
        return current

    '''creates immediate next moves for current node'''
    def expansion(self, leaf):
        children = self.sim_board.get_all_possible_moves(self.opponent[leaf._turn])
        temp_child = None
        # print("These are children in expansion:", children)
        # print("leaf:", leaf)
        for moves_for_piece in children: #moves_for_piece is a list of moves (as Move objects) for one piece e.g: [(5,2)-(4,1), (5,2)-(4,3)]
            for my_move in moves_for_piece: #my_move is Move Object e.g: (5,2)-(4,1)
                temp_child = TreeNode(parent = leaf, children = [], move = my_move, turn = self.opponent[leaf.turn()])
                # print("temp_child:", temp_child)
                # print("temp_child's children:", temp_child.children())
                leaf._children.append(temp_child)

    '''picks children with highest UCT until reaches end of game
        for enemy's turn, we use heuristic value (piece count) to determine which move to pick'''
    def simulation(self, leaf):
        tie_max = 20
        current = leaf
        tie_counter = 0 # i think having our own tie counter instead of waiting till 40 every game can speed up simulations alot
        counter = 0
        while not self.sim_board.is_win(current._turn) and tie_counter < tie_max and counter < 41:
            # print("my current:", current)
            self.expansion(current)
            # print("this is current children:", current.children())
            #this means all the children are capture
            if abs(current._children[0]._move[1][0] - current._children[0]._move[0][0]) > 1:
                # print("test")
                tie_counter = 0
                current._wins -= 0.6
                current, length_of_capture = current.pick_child_capture()
                current.add_capture(2, 0.3*length_of_capture) #change depth later to a counter?
            else:
                # print("other")
                tie_counter += 1
                current = current.pick_child_random()
            # self.sim_board.show_board()
            # print(counter, current._move)
            # print(current._turn)
            self.sim_board.make_move(current._move, current._turn)
            counter += 1
        if tie_counter > tie_max:
            # print("tie")
            return current, self.color
        # print("not a tie")
        return current, self.sim_board.is_win(current.turn())


    '''once we reach terminal node (end of game node or leaf node), we travel upwards to our root and update all the nodes along the way'''
    # def backtracking(self, node, winner):
    #     # loop for winning moves
    #     current = node
    #     while current._move and current != self.root:
    #         # print("backtracking:", current)
    #         if current._turn == winner:
    #             current._wins += 1
    #         elif winner == -1:
    #             current._wins += 0.75
    #         current._games += 1
    #         current = current._parent
    #         self.sim_board.undo()
    #     self.root._games += 1
    #     if self.root._turn == winner: #i dont think we have to update roots wins since its a move that already happened
    #         self.root._wins += 1


    ''' I think this version is faster since it halves the number of comparisons
    the code now knows which nodes win and lose from one comparison at the start
    rather than checking if the node won or lost when visiting each node
    it is a lot uglier though
    i can definitely abstract the sections into a helper function if we choose to use this
    '''
    def backtracking(self, node, winner):
        # print(node, winner)
        current = node
        if winner == -1 or winner == 0:
            # print("first")
            while current._move and current != self.root:
                current._wins += 0.8
                current._games += 1
                current = current._parent
                self.sim_board.undo()
        elif current._turn == winner:
            # print("second")
            while current._move:
                if current == self.root:
                    break
                else:
                    current._wins += 1
                    current._games += 1
                    current = current._parent
                    self.sim_board.undo()
                if current == self.root:
                    break
                else:
                    current._games += 1
                    current = current._parent
                    self.sim_board.undo()
        elif self.opponent[current._turn] == winner:
            # print("third")
            while current._move:
                if current == self.root:
                    break
                else:
                    current._games += 1
                    current = current._parent
                    self.sim_board.undo()
                if current == self.root:
                    break
                else:
                    current._wins += 1
                    current._games += 1
                    current = current._parent
                    self.sim_board.undo()
                    
        self.root._games += 1


class TreeNode:
    def __init__(self, parent=None, children=[], move=None, turn=None):
        self._parent = parent
        self._children = children
        self._move = move
        self._wins = 0
        self._games = 0
        self._turn = turn

    def __str__(self):
        result = 'Node('
        if not self.parent:
            return 'root_node()'
        # result += f'Num_Children: {len(self._children)}, Move: {self._move}, Turn: {self._turn})'
        result += 'Num_Children: '
        result += str(len(self._children))
        result += ', Move: '
        result += str(self._move)
        result += ', Turn: '
        result += str(self._turn) + ')'
        return result
    
    def __repr__(self):
        return str(self)

    def parent(self) -> 'TreeNode':
        return self._parent

    def children(self):
        return self._children

    def wins(self) -> int:
        return self._wins

    def move(self):
        return self._move

    def turn(self):
        return self._turn

    '''picks child with largest UCT'''
    def pick_child(self, c: float):
        max_uct = -1
        max_child = None
        parent_wins = self._wins
        # iterates through all of a nodes children, assigning uct values
        # keeps track of max as it goes
        for child in self._children:
            # wins = child.wins()
            # games = child.games()
            uct = child.UCT(c)  # 1 is the c parameter
            if uct > max_uct:
                max_uct = uct
                max_child = child

        return max_child

    def pick_child_random(self):
        child = randint(0, len(self._children) - 1)
        return self._children[child]

    def pick_child_capture(self):
        max_length = -1
        max_child = 0
        for i in range(len(self._children)):
            current = len(self._children[i]._move)
            if (current > max_length):
                max_length = current
                max_child = i 
        
        return self._children[max_child], max_length

    def pick_best_child(self):
        best_child = None
        best_wr = -1
        for child in self._children:
            wr = child._wins / child._games
            if wr > best_wr:
                best_wr = wr
                best_child = child
        return best_child


    def has_parent(self):
        return self._parent is not None


    def increment_wins(self):
        self._wins += 1

    def games(self) -> int:
        return self._games
    
    def UCT(self, c: float) -> float:
        if self._parent is None:
            return -1
        if self._games == 0:
            return 999
        # if self._parent.games() == 0:
        #     return 999
        # print("wins:", self._wins, "games:", self._games, "parent_games:", self._parent.games())
        return (self._wins / self._games) + c * sqrt(log(self._parent._games) / self._games)
    
    def add_child(self, new_child: 'TreeNode'):
        self._children.append(new_child)

    def update_move(self, new_move):
        self._move = new_move

    def add_win(self):
        self._wins += 1

    def add_tie(self):
        self._wins += .75

    def add_capture(self, depth, reward):
        for i in range(1, depth + 1):
            parent = self.parent()  # this is the enemies move that led to capture
            parent._wins += -1 * reward / depth  # decentivizes this move for enemy since it led to capture

            parent = self.parent()  # this is our move that put us in the state to capture
            parent._wins += reward / depth  # incentivizes the move for our ai

    def add_game(self):
        self._games += 1

    def update_turn(self, new_turn):
        self._turn = new_turn



