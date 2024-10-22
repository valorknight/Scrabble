import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
import random
from collections import defaultdict

# Tile distribution and points
TILE_DISTRIBUTION = {
    'A': 9, 'B': 2, 'C': 2, 'D': 4, 'E': 12, 'F': 2, 'G': 3, 'H': 2, 'I': 9, 'J': 1, 'K': 1,
    'L': 4, 'M': 2, 'N': 6, 'O': 8, 'P': 2, 'Q': 1, 'R': 6, 'S': 4, 'T': 6, 'U': 4, 'V': 2,
    'W': 2, 'X': 1, 'Y': 2, 'Z': 1, '_': 2  # Blanks are represented as '_'
}

POINTS = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8, 'K': 5,
    'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4,
    'W': 4, 'X': 8, 'Y': 4, 'Z': 10, '_': 0  # Blanks score 0 points
}

# Word dictionary
#kindly download the words txt file and rename it to the necessary file location
f_op = open(r'PROJETC\words.txt')
SCRABBLE_DICTIONARY = f_op.read().split()

#The game
class ScrabbleGUI:
    def __init__(self, master, num_players=2):
        self.master = master
        self.master.title("Scrabble Game")
        self.board_size = 15
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.tile_bag = self._generate_tile_bag()
        self.players = {f'Player {i+1}': {'tiles': [], 'score': 0} for i in range(num_players)}
        self.current_player = 0
        self.selected_tile = None
        self.placed_tiles = defaultdict(str)
        self.tiles_played_in_turn = []  # Stores tiles played during current turn

        self.create_board()
        self.create_player_area()
        self.create_buttons()
        self._deal_tiles()
        self.update_player_display()

    #Tile bag
    def _generate_tile_bag(self):
        tiles = [letter for letter, count in TILE_DISTRIBUTION.items() for _ in range(count)]
        random.shuffle(tiles)
        return tiles

    def _deal_tiles(self):
        for player in self.players:
            while len(self.players[player]['tiles']) < 7 and self.tile_bag:
                self.players[player]['tiles'].append(self.tile_bag.pop())

    #Board creation
    def create_board(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                button = tk.Button(
                    self.master,
                    width=3, height=1, text="", font=("Arial", 12),  # Fixed size font
                    command=lambda r=row, c=col: self.on_board_click(r, c)
                )
                button.grid(row=row, column=col)
                self.board[row][col] = button

    def create_player_area(self):
        self.player_frame = tk.Frame(self.master)
        self.player_frame.grid(row=16, columnspan=15)

        self.player_labels = {}
        for i, player in enumerate(self.players.keys()):
            label = tk.Label(self.player_frame, text=f"{player}: ", font=("Arial", 12))
            label.grid(row=i, column=0, sticky='w')
            self.player_labels[player] = tk.Label(self.player_frame, text="", font=("Arial", 12))
            self.player_labels[player].grid(row=i, column=1, sticky='w')

        self.tile_buttons = []
        for i in range(7):  # Player can have 7 tiles
            btn = tk.Button(self.player_frame, text="", width=4, height=2, font=("Arial", 12), command=lambda i=i: self.select_tile(i))
            btn.grid(row=0, column=i + 2)
            self.tile_buttons.append(btn)

    def create_buttons(self):
        self.next_turn_button = tk.Button(self.master, text="Next Turn", command=self.next_turn)
        self.next_turn_button.grid(row=17, columnspan=15, pady=10)

        self.retry_button = tk.Button(self.master, text="Retry Move", command=self.retry_move, state=tk.DISABLED)
        self.retry_button.grid(row=18, columnspan=15, pady=10)

    def update_player_display(self):
        player = f'Player {self.current_player + 1}'
        for i, tile in enumerate(self.players[player]['tiles']):
            self.tile_buttons[i].config(text=tile, state=tk.NORMAL)

        for i in range(len(self.players[player]['tiles']), 7):
            self.tile_buttons[i].config(text="", state=tk.DISABLED)

        for player_name in self.players.keys():
            tiles_str = ' '.join(self.players[player_name]['tiles'])
            self.player_labels[player_name].config(text=f"Tiles: {tiles_str} | Score: {self.players[player_name]['score']}")
    # Selecting Tile
    def select_tile(self, tile_index):
        player = f'Player {self.current_player + 1}'
        self.selected_tile = (tile_index, self.players[player]['tiles'][tile_index])
    #Playing tile
    def on_board_click(self, row, col):
        if self.selected_tile is None:
            return

        player = f'Player {self.current_player + 1}'
        if self.board[row][col].cget("text") == "":
            tile_index, letter = self.selected_tile

            # This is for blank tiles
            if letter == '_':
                letter = simpledialog.askstring("Blank Tile", "Enter the letter you want this blank tile to represent:")
                if not letter or len(letter) != 1 or not letter.isalpha():
                    messagebox.showerror("Invalid Input", "Please enter a single valid letter.")
                    return
                letter = letter.upper()

            # Replace the button text with the chosen letter
            self.board[row][col].config(text=letter, font=("Arial", 12))  # Ensure font size is fixed
            self.placed_tiles[(row, col)] = letter
            self.tiles_played_in_turn.append((tile_index, letter))  # Track the played tile for reset if needed
            self.players[player]['tiles'].pop(tile_index)
            self.selected_tile = None
            self.update_player_display()

    #Check for valid word or not
    def validate_word(self):
        words = self._get_formed_words()
        for word in words:
            if word not in SCRABBLE_DICTIONARY:
                return False
        return True

    def validate_adjacency(self):
        if len(self.placed_tiles) == 0:
            return False

        # Check if it is the first move
        is_first_move = all(self.board[row][col].cget("text") == "" for row in range(self.board_size) for col in range(self.board_size))
        if is_first_move:
            return True  # For the first move, it's allowed to place anywhere.

        adjacent_to_existing = False
        for (row, col), letter in self.placed_tiles.items():
            if (row > 0 and self.board[row-1][col].cget("text") != "") or \
               (row < self.board_size - 1 and self.board[row+1][col].cget("text") != "") or \
               (col > 0 and self.board[row][col-1].cget("text") != "") or \
               (col < self.board_size - 1 and self.board[row][col+1].cget("text") != ""):
                adjacent_to_existing = True

        if not adjacent_to_existing:
            messagebox.showerror("Invalid Placement", "Tiles must be adjacent to an existing word.")
            return False

        return True

    def _get_formed_words(self):
        words = set()
        for (row, col), letter in self.placed_tiles.items():
            word_horizontal = self._get_word(row, col, direction='horizontal')
            if len(word_horizontal) > 1:
                words.add(word_horizontal)
            word_vertical = self._get_word(row, col, direction='vertical')
            if len(word_vertical) > 1:
                words.add(word_vertical)
        return words

    def _get_word(self, row, col, direction='horizontal'):
        word = ""
        if direction == 'horizontal':
            start_col = col
            while start_col > 0 and self.board[row][start_col - 1].cget("text") != "":
                start_col -= 1
            while start_col < self.board_size and self.board[row][start_col].cget("text") != "":
                word += self.board[row][start_col].cget("text")
                start_col += 1
        elif direction == 'vertical':
            start_row = row
            while start_row > 0 and self.board[start_row - 1][col].cget("text") != "":
                start_row -= 1
            while start_row < self.board_size and self.board[start_row][col].cget("text") != "":
                word += self.board[start_row][col].cget("text")
                start_row += 1
        return word

    #criteria for next turn
    def next_turn(self):
        if not self.validate_adjacency():
            return
        if not self.validate_word():
            messagebox.showerror("Invalid Word", "One or more words are invalid. Please retry.")
            self.retry_button.config(state=tk.NORMAL)
            return

        # Calculate score for the current player
        player = f'Player {self.current_player + 1}'
        score = sum(POINTS[letter] for (row, col), letter in self.placed_tiles.items())
        self.players[player]['score'] += score

        # Clear placed tiles for next turn
        self.placed_tiles.clear()
        self.tiles_played_in_turn.clear()

        # Refill player tiles and move to the next player
        self._deal_tiles()
        self.current_player = (self.current_player + 1) % len(self.players)
        self.update_player_display()

    def retry_move(self):
        # Reset board for the current turn
        for (row, col), letter in self.placed_tiles.items():
            self.board[row][col].config(text="")
        
        # Restore the tiles back to the player
        player = f'Player {self.current_player + 1}'
        for tile_index, letter in self.tiles_played_in_turn:
            self.players[player]['tiles'].insert(tile_index, letter)

        self.placed_tiles.clear()
        self.tiles_played_in_turn.clear()
        self.update_player_display()

        self.retry_button.config(state=tk.DISABLED)


# Start the game
root = tk.Tk()
game = ScrabbleGUI(root, num_players=2)
root.mainloop()
