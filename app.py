from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import random
import string
import json
import math
import time

app = Flask(__name__)
CORS(app)

# ============================================================
# WORDLE GAME
# ============================================================
WORD_LIST = [
    "apple", "berry", "cherry", "dragon", "eagle", "frank", "grape",
    "honey", "ilium", "jelly", "kangaroo", "lemon", "mango", "nutmeg",
    "orange", "peach", "queen", "raspberry", "strawberry", "tangerine",
    "umber", "vanilla", "watermelon", "xenon", "yacht", "zebra"
]

def get_random_word():
    return random.choice(WORD_LIST)

# ============================================================
# SPELLING BEE GAME
# ============================================================
def generate_spelling_bee_grid():
    """Generate a 7-letter honeycomb grid with center letter."""
    vowels = set("aeiou")
    consonants = "bcdfghjklmnpqrstvwxyz"
    
    center = random.choice(tuple(vowels))
    remaining_vowels = list(vowels - {center})
    others = random.sample(consonants, 3) + random.sample(remaining_vowels, 3)
    random.shuffle(others)
    
    grid = [center] + others
    return grid, center

def is_valid_spelling_bee_word(word, grid, center):
    if len(word) < 4:
        return False
    if center not in word.lower():
        return False
    word_set = set(word.lower())
    for letter in word_set:
        if letter not in grid:
            return False
    return True

# ============================================================
# CONNECTIONS GAME (16 words, 4 categories of 4)
# ============================================================
def get_connections_words():
    all_words = [
        "apple", "banana", "carrot", "donut", "egg", "flour", "grape",
        "honey", "ice", "jam", "knife", "lemon", "melon", "nut", "olive",
        "pie", "quiche", "rice", "sugar", "tea", "umbrella", "vanilla",
        "wine", "xigua", "yam", "zucchini"
    ]
    selected = random.sample(all_words, 16)
    
    categories = {
        "YELLOW": selected[0:4],
        "GREEN": selected[4:8],
        "BLUE": selected[8:12],
        "PURPLE": selected[12:16]
    }
    
    return selected, categories

def check_connections_guess(selected_groups):
    pass

# ============================================================
# SUDOKU GAME
# ============================================================
def generate_sudoku():
    grid = [[0]*9 for _ in range(9)]
    
    def is_valid(grid, row, col, num):
        for x in range(9):
            if grid[row][x] == num or grid[x][col] == num:
                return False
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if grid[i][j] == num:
                    return False
        return True
    
    def solve(grid):
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    for num in range(1, 10):
                        if is_valid(grid, i, j, num):
                            grid[i][j] = num
                            if solve(grid):
                                return True
                            grid[i][j] = 0
                    return False
        return True
    
    solve(grid)
    
    puzzle = [row[:] for row in grid]
    cells = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(cells)
    for i, j in cells[40:]:
        puzzle[i][j] = 0
    
    return puzzle, grid

# ============================================================
# MINI CROSSWORD GAME
# ============================================================
def generate_mini_crossword():
    words = ["hello", "world", "python", "flask", "games", "code", "fun"]
    
    grid = [[""] * 5 for _ in range(5)]
    clues_across = []
    clues_down = []
    
    for i, letter in enumerate("python"):
        grid[2][i] = letter
    clues_across.append(("Across 1", "A programming language"))
    
    for i, letter in enumerate("hello"):
        grid[i][4] = letter
    clues_down.append(("Down 1", "A greeting"))
    
    return grid, clues_across, clues_down

# ============================================================
# 2048 GAME
# ============================================================
def new_2048_game():
    grid = [[0]*4 for _ in range(4)]
    for _ in range(2):
        empty = [(r, c) for r in range(4) for c in range(4) if grid[r][c] == 0]
        if empty:
            r, c = random.choice(empty)
            grid[r][c] = 2 if random.random() < 0.9 else 4
    return grid

def move_2048(grid, direction):
    return grid, 0

# ============================================================
# MINESWEEPER GAME
# ============================================================
def new_minesweeper(game_size=9, num_mines=10):
    grid = [[0]*game_size for _ in range(game_size)]
    mines = set()
    
    while len(mines) < num_mines:
        r = random.randint(0, game_size-1)
        c = random.randint(0, game_size-1)
        mines.add((r, c))
    
    for r, c in mines:
        grid[r][c] = -1
    
    for r in range(game_size):
        for c in range(game_size):
            if grid[r][c] != -1:
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r+dr, c+dc
                        if 0 <= nr < game_size and 0 <= nc < game_size and grid[nr][nc] == -1:
                            count += 1
                grid[r][c] = count
    
    return grid

# ============================================================
# FLASK ROUTES
# ============================================================
@app.route('/')
def index():
    return render_template('index.html')

# Wordle routes
@app.route('/api/wordle/new', methods=['GET'])
def wordle_new():
    word = get_random_word()
    masked = '_' * len(word)
    return jsonify({
        'word_length': len(word),
        'mask': masked,
        'game': 'wordle'
    })

@app.route('/api/wordle/guess', methods=['POST'])
def wordle_guess():
    data = request.get_json()
    guess = data.get('guess', '').lower()
    return jsonify({'guess': guess, 'status': 'processing'})

# Spelling Bee routes
@app.route('/api/spelling-bee/new', methods=['GET'])
def spelling_bee_new():
    grid, center = generate_spelling_bee_grid()
    return jsonify({
        'grid': grid,
        'center': center,
        'game': 'spelling-bee'
    })

@app.route('/api/spelling-bee/validate', methods=['POST'])
def spelling_bee_validate():
    data = request.get_json()
    word = data.get('word', '').lower()
    grid = data.get('grid', [])
    center = data.get('center', '')
    valid = is_valid_spelling_bee_word(word, grid, center)
    return jsonify({'word': word, 'valid': valid, 'game': 'spelling-bee'})

# Connections routes
@app.route('/api/connections/new', methods=['GET'])
def connections_new():
    words, categories = get_connections_words()
    return jsonify({
        'words': words,
        'categories': categories,
        'game': 'connections'
    })

@app.route('/api/connections/guess', methods=['POST'])
def connections_guess():
    data = request.get_json()
    groups = data.get('groups', [])
    return jsonify({'groups': groups, 'status': 'checking'})

# Sudoku routes
@app.route('/api/sudoku/new', methods=['GET'])
def sudoku_new():
    puzzle, solution = generate_sudoku()
    return jsonify({
        'puzzle': puzzle,
        'game': 'sudoku'
    })

@app.route('/api/sudoku/check', methods=['POST'])
def sudoku_check():
    data = request.get_json()
    puzzle = data.get('puzzle', [])
    return jsonify({'valid': True, 'game': 'sudoku'})

# Mini Crossword routes
@app.route('/api/crossword/new', methods=['GET'])
def crossword_new():
    grid, clues_across, clues_down = generate_mini_crossword()
    return jsonify({
        'grid': grid,
        'clues_across': clues_across,
        'clues_down': clues_down,
        'game': 'crossword'
    })

# 2048 routes
@app.route('/api/2048/new', methods=['GET'])
def twenty48_new():
    grid = new_2048_game()
    return jsonify({
        'grid': grid,
        'score': 0,
        'game': '2048'
    })

@app.route('/api/2048/move', methods=['POST'])
def twenty48_move():
    data = request.get_json()
    grid = data.get('grid', [])
    direction = data.get('direction', 'left')
    new_grid, score = move_2048(grid, direction)
    return jsonify({'grid': new_grid, 'score': score, 'game': '2048'})

# Minesweeper routes
@app.route('/api/minesweeper/new', methods=['GET'])
def minesweeper_new():
    grid = new_minesweeper()
    return jsonify({
        'grid': grid,
        'game': 'minesweeper'
    })

@app.route('/api/minesweeper/click', methods=['POST'])
def minesweeper_click():
    data = request.get_json()
    r, c = data.get('row', 0), data.get('col', 0)
    return jsonify({'row': r, 'col': c, 'game': 'minesweeper'})

if __name__ == '__main__':
    print("Cacak Times starting...")
    print("Visit http://localhost:5000 to access the games")
    app.run(host='0.0.0.0', port=5000, debug=True)
