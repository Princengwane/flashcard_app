import pandas as pd
from flask import Flask, render_template, request, jsonify
import datetime
import random

# Initialize Flask app
app = Flask(__name__)

# Load the mistakes data
data = pd.read_csv("mistakes.csv")

# Spaced Repetition Parameters
EASE_FACTOR = 2.5
INTERVAL = 1
REPETITIONS = 0
GRADE = 0
NEXT_REVIEW = datetime.date.today()

# Store flashcards in memory for simplicity (normally you would use a database)
flashcards = []

# Function to generate flashcards
def generate_flashcards():
    global flashcards
    flashcards = []
    for _, row in data.iterrows():
        flashcard = {
            "question": f"Why is '{row['Original_Sentence']}' incorrect?",
            "answer": row['Corrected_Sentence'],
            "type": row['Mistake_Type'],
            "difficulty": 1,  # Initially set to 1
            "next_review": datetime.date.today(),
        }
        flashcards.append(flashcard)

# SM2 algorithm for spaced repetition
def update_flashcard(flashcard, grade):
    global EASE_FACTOR, INTERVAL, REPETITIONS, NEXT_REVIEW
    
    # Update ease factor and interval based on the grade
    EASE_FACTOR = EASE_FACTOR + 0.1 * (5 - grade)
    INTERVAL = max(1, INTERVAL * EASE_FACTOR)
    
    # Update repetition count
    if grade >= 3:
        REPETITIONS += 1
    else:
        REPETITIONS = 1
    
    # Set the next review date based on the interval
    NEXT_REVIEW = datetime.date.today() + datetime.timedelta(days=INTERVAL)
    
    flashcard['ease_factor'] = EASE_FACTOR
    flashcard['interval'] = INTERVAL
    flashcard['repetitions'] = REPETITIONS
    flashcard['next_review'] = NEXT_REVIEW
    return flashcard

# Generate flashcards when the app starts
generate_flashcards()

@app.route('/')
def index():
    return render_template('index.html', flashcards=flashcards)

@app.route('/answer', methods=['POST'])
def answer():
    flashcard_id = int(request.form['flashcard_id'])
    grade = int(request.form['grade'])
    
    flashcard = flashcards[flashcard_id]
    updated_flashcard = update_flashcard(flashcard, grade)
    
    return jsonify({
        "message": f"Flashcard updated. Next review: {updated_flashcard['next_review']}",
        "flashcard": updated_flashcard
    })

if __name__ == "__main__":
    app.run(debug=True)
