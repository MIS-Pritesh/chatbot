# api.py (FastAPI application for Vercel)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from collections import OrderedDict

# ======================================================================
# 1. DATA LOADING AND PROCESSING (Modified for Serverless function)
# ======================================================================

CSV_FILE_NAME = "Data.csv" 
# Use a global variable to cache the data outside of any request handling function
GLOBAL_QA_DATA = {}

def load_and_structure_data(file_name):
    """
    Loads data from CSV and structures it once.
    """
    # Vercel deployment root path (where Data.csv will be found)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, file_name)
    
    if not os.path.exists(file_path):
        print(f"FATAL ERROR: Data file '{file_name}' not found at {file_path}")
        return {}
    
    try:
        df = pd.read_csv(file_path)
        REQUIRED_COLS = ['subject', 'question', 'answer']
        if not all(col in df.columns for col in REQUIRED_COLS):
            print(f"FATAL ERROR: CSV must contain the columns: {', '.join(REQUIRED_COLS)}")
            return {}
        
        main_menu = OrderedDict() 
        sub_menus = {}
        grouped_data = df.groupby('subject')
        
        for subject, group in grouped_data:
            key = str(len(main_menu) + 1)
            main_menu[key] = subject
            
            sub_menu_questions = OrderedDict()
            for i, row in enumerate(group.itertuples()):
                sub_menu_questions[row.question] = row.answer # Store question as key, answer as value
            
            sub_menus[subject] = sub_menu_questions

        return {
            'main_menu': list(main_menu.values()), # Just the subject names
            'sub_menus': sub_menus,
            'qa_data_df': df # Keep the DataFrame for quick lookup
        }

    except Exception as e:
        print(f"FATAL ERROR: Failed to load or process CSV data. Error: {e}")
        return {}

# Load data when the API starts up (which happens once per Vercel serverless instance)
GLOBAL_QA_DATA = load_and_structure_data(CSV_FILE_NAME)


# ======================================================================
# 2. FASTAPI APP SETUP
# ======================================================================

app = FastAPI()

# Add CORS middleware for frontend access (if you ever build a separate frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust this in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======================================================================
# 3. API ENDPOINTS
# ======================================================================

@app.get("/")
def read_root():
    return {"status": "PlotBot API is running!", "endpoints": ["/menu", "/answer/{question}"]}

@app.get("/menu")
def get_main_menu():
    """Returns the list of main categories (subjects)."""
    if 'main_menu' not in GLOBAL_QA_DATA:
        return {"error": "Data not loaded"}, 500
    return GLOBAL_QA_DATA['main_menu']

@app.get("/questions/{subject}")
def get_sub_menu(subject: str):
    """Returns questions for a specific subject/category."""
    if 'sub_menus' not in GLOBAL_QA_DATA:
        return {"error": "Data not loaded"}, 500
    
    questions = list(GLOBAL_QA_DATA['sub_menus'].get(subject, {}).keys())
    
    if not questions:
        return {"error": f"Subject '{subject}' not found"}, 404
    
    return questions

@app.get("/answer")
def get_fixed_answer(question: str):
    """Retrieves the answer for a specific question."""
    if GLOBAL_QA_DATA.get('qa_data_df') is None:
        return {"error": "Data not loaded"}, 500
        
    try:
        # FastAPI's request handling is stateless, so we look up the answer directly
        df = GLOBAL_QA_DATA['qa_data_df']
        answer_row = df[df['question'] == question]
        
        if not answer_row.empty:
            return {"question": question, "answer": answer_row.iloc[0]['answer']}
        
        return {"question": question, "answer": "I'm sorry, I could not find a specific answer for that question in my database."}
        
    except Exception as e:
        return {"error": f"An internal error occurred during lookup: {e}"}, 500
