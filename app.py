from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np

app = FastAPI()

# Pydantic models for request/response
class Move(BaseModel):
    row: int
    col: int
    player: str

class GameState(BaseModel):
    board: list[list[str]]
    current_player: str
    winner: str | None
    is_draw: bool

# In-memory game state
game_state = {
    "board": [["" for _ in range(3)] for _ in range(3)],
    "current_player": "X",
    "winner": None,
    "is_draw": False
}

def check_winner(board: list[list[str]]) -> str | None:
    board_array = np.array(board)
    # Check rows
    for row in board_array:
        if len(set(row)) == 1 and row[0] != "":
            return row[0]
    # Check columns
    for col in board_array.T:
        if len(set(col)) == 1 and col[0] != "":
            return col[0]
    # Check diagonals
    if len(set(board_array.diagonal())) == 1 and board_array[0, 0] != "":
        return board_array[0, 0]
    if len(set(np.fliplr(board_array).diagonal())) == 1 and board_array[0, 2] != "":
        return board_array[0, 2]
    return None

def check_draw(board: list[list[str]]) -> bool:
    return all(cell != "" for row in board for cell in row)

@app.get("/game", response_model=GameState)
async def get_game_state():
    return game_state

@app.post("/move", response_model=GameState)
async def make_move(move: Move):
    if move.player not in ["X", "O"]:
        raise HTTPException(status_code=400, detail="Player must be X or O")
    if move.player != game_state["current_player"]:
        raise HTTPException(status_code=400, detail="Not your turn")
    if move.row < 0 or move.row > 2 or move.col < 0 or move.col > 2:
        raise HTTPException(status_code=400, detail="Invalid position")
    if game_state["board"][move.row][move.col] != "":
        raise HTTPException(status_code=400, detail="Position already taken")
    if game_state["winner"] or game_state["is_draw"]:
        raise HTTPException(status_code=400, detail="Game is over")

    # Update board
    game_state["board"][move.row][move.col] = move.player
    
    # Check for winner or draw
    game_state["winner"] = check_winner(game_state["board"])
    game_state["is_draw"] = check_draw(game_state["board"]) and not game_state["winner"]
    
    # Switch player
    if not game_state["winner"] and not game_state["is_draw"]:
        game_state["current_player"] = "O" if move.player == "X" else "X"
    
    return game_state

@app.post("/reset", response_model=GameState)
async def reset_game():
    game_state["board"] = [["" for _ in range(3)] for _ in range(3)]
    game_state["current_player"] = "X"
    game_state["winner"] = None
    game_state["is_draw"] = False
    return game_state