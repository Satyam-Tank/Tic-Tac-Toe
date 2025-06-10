import streamlit as st
import requests
import json

API_URL = "http://localhost:8000"

def get_game_state():
    response = requests.get(f"{API_URL}/game")
    return response.json()

def make_move(row, col, player):
    response = requests.post(f"{API_URL}/move", json={"row": row, "col": col, "player": player})
    return response.json()

def reset_game():
    response = requests.post(f"{API_URL}/reset")
    return response.json()

st.title("Tic-Tac-Toe")

# Initialize session state
if "game_state" not in st.session_state:
    st.session_state.game_state = get_game_state()

# Display game status
if st.session_state.game_state["winner"]:
    st.success(f"Player {st.session_state.game_state['winner']} wins!")
elif st.session_state.game_state["is_draw"]:
    st.warning("Game is a draw!")
else:
    st.info(f"Player {st.session_state.game_state['current_player']}'s turn")

# Display game board
for row in range(3):
    cols = st.columns(3)
    for col in range(3):
        cell_value = st.session_state.game_state["board"][row][col]
        button_label = cell_value if cell_value else " "
        disabled = cell_value != "" or st.session_state.game_state["winner"] or st.session_state.game_state["is_draw"]
        if cols[col].button(button_label, key=f"cell_{row}_{col}", disabled=disabled):
            try:
                st.session_state.game_state = make_move(row, col, st.session_state.game_state["current_player"])
            except requests.exceptions.RequestException as e:
                st.error(f"Error making move: {e}")

# Reset button
if st.button("Reset Game"):
    st.session_state.game_state = reset_game()

# Refresh game state
if st.button("Refresh"):
    st.session_state.game_state = get_game_state()