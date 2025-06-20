import json
import os

def save_game(game_state, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(game_state, f, ensure_ascii=False, indent=2)

def load_game(filename):
    if not os.path.exists(filename):
        return None
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def delete_save(filename):
    if os.path.exists(filename):
        os.remove(filename) 