import tkinter as tk
from tkinter import messagebox
import copy

class GameState:
    def __init__(self, p1_pits, p2_pits, p1_store, p2_store, turn, current_player):
        self.p1_pits = p1_pits.copy()
        self.p2_pits = p2_pits.copy()
        self.p1_store = p1_store
        self.p2_store = p2_store
        self.turn = turn
        self.current_player = current_player

    def is_terminal(self):
        return all(count == 0 for count in self.p1_pits) or all(count == 0 for count in self.p2_pits)

    def get_legal_moves(self):
        moves = []
        if self.current_player == 2 and self.turn == 2:
            moves.append("PIE")
        pits = self.p1_pits if self.current_player == 1 else self.p2_pits
        for i in range(6):
            if pits[i] > 0:
                moves.append(i + 1)
        return moves

    def apply_move(self, move):
        new_state = copy.deepcopy(self)
        if move == "PIE":
            new_state.p1_pits, new_state.p2_pits = new_state.p2_pits, new_state.p1_pits
            new_state.p1_store, new_state.p2_store = new_state.p2_store, new_state.p1_store
            new_state.current_player = 1
            new_state.turn += 1
            return new_state

        pits = new_state.p1_pits if new_state.current_player == 1 else new_state.p2_pits
        index = move - 1
        stones = pits[index]
        pits[index] = 0

        i = index
        while stones > 0:
            i = (i + 1) % 6
            pits[i] += 1
            stones -= 1

        new_state.current_player = 2 if new_state.current_player == 1 else 1
        new_state.turn += 1
        return new_state

# UI Code
class MancalaUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mancala Game")
        self.state = GameState([4]*6, [4]*6, 0, 0, 1, 1)
        self.status_label = tk.Label(root, text="")
        self.status_label.pack()
        self.board_frame = tk.Frame(root)
        self.board_frame.pack()
        self.update_ui()

    def make_move(self, move):
        self.state = self.state.apply_move(move)
        self.update_ui()
        if self.state.is_terminal():
            winner = "Player 1" if self.state.p1_store > self.state.p2_store else "Player 2" if self.state.p2_store > self.state.p1_store else "No one"
            messagebox.showinfo("Game Over", f"{winner} wins!")

    def update_ui(self):
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        legal_moves = self.state.get_legal_moves()
        self.status_label.config(text=f"Player {self.state.current_player}'s Turn")

        # Top row - Player 2 pits
        tk.Label(self.board_frame, text=f"P2 Store: {self.state.p2_store}", width=10).grid(row=0, column=0)
        for i in range(6):
            tk.Label(self.board_frame, text=str(self.state.p2_pits[i]), width=10).grid(row=0, column=i + 1)

        # Bottom row - Player 1 pits and buttons
        for i in range(6):
            m = i + 1
            btn = tk.Button(self.board_frame, text=str(self.state.p1_pits[i]), width=10,
                            command=lambda m=m: self.make_move(m))
            btn.grid(row=2, column=i + 1)
            if m not in legal_moves:
                btn.config(state='disabled')

        tk.Label(self.board_frame, text=f"P1 Store: {self.state.p1_store}", width=10).grid(row=2, column=0)

        # PIE move
        if "PIE" in legal_moves:
            pie_button = tk.Button(self.board_frame, text="PIE Move", width=10, command=lambda: self.make_move("PIE"))
            pie_button.grid(row=1, column=3, columnspan=2)

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    app = MancalaUI(root)
    root.mainloop()