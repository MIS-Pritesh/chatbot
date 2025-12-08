import streamlit as st
import pandas as pd
import os
from collections import OrderedDict

# ======================================================================
# 1. DATA LOADING AND PROCESSING
# ======================================================================

# File name must match your GitHub file name exactly
CSV_FILE_NAME = "Data.csv" 

@st.cache_data
def load_and_structure_data(file_name):
    """
    Loads data from CSV, structures it into an organized dictionary
    for menu display, and returns the main subjects and sub-menus.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)
    
    if not os.path.exists(file_path):
        st.error(f"FATAL ERROR: Data file '{file_name}' not found.")
        return OrderedDict(), {}, pd.DataFrame()
    
    try:
        df = pd.read_csv(file_path)
        REQUIRED_COLS = ['subject', 'question', 'answer']
        if not all(col in df.columns for col in REQUIRED_COLS):
            st.error(f"FATAL ERROR: CSV must contain the columns: {', '.join(REQUIRED_COLS)}")
            return OrderedDict(), {}, pd.DataFrame()
        
        main_menu = OrderedDict() 
        sub_menus = {}
        grouped_data = df.groupby('subject')
        
        for subject, group in grouped_data:
            key = str(len(main_menu) + 1)
            main_menu[key] = subject
            
            sub_menu_questions = OrderedDict()
            for i, row in enumerate(group.itertuples()):
                q_key = str(i + 1)
                sub_menu_questions[q_key] = row.question
            
            sub_menus[subject] = sub_menu_questions

        return main_menu, sub_menus, df

    except Exception as e:
        st.error(f"FATAL ERROR: Failed to load or process CSV data. Error: {e}")
        return OrderedDict(), {}, pd.DataFrame()

# Load data only once at the start of the session
if 'main_menu' not in st.session_state:
    main_menu_data, sub_menus_data, qa_data_df = load_and_structure_data(CSV_FILE_NAME)
    st.session_state.main_menu = main_menu_data
    st.session_state.sub_menus = sub_menus_data
    st.session_state.qa_data = qa_data_df


# ======================================================================
# 2. ANSWER RETRIEVAL LOGIC
# ======================================================================

def get_fixed_answer(question):
    """Retrieves the answer by searching the loaded DataFrame."""
    if 'qa_data' not in st.session_state or st.session_state.qa_data.empty:
        return "System error: Data not loaded."
        
    try:
        answer_row = st.session_state.qa_data[st.session_state.qa_data['question'] == question]
        
        if not answer_row.empty:
            return answer_row.iloc[0]['answer']
        
        return "I'm sorry, I could not find a specific answer for that question in my database."
    except Exception as e:
        return f"An internal error occurred during lookup: {e}"


# ======================================================================
# 3. THEME AND CSS INJECTION
# ======================================================================

# --- CSS to Hide the Overwritten Message ---
# We use CSS to hide any chat message that contains the zero-width space (\u200B).
def inject_final_css():
    css = """
    /* Default Theme */
    :root {
        --primary-color: #4CAF50; 
        --background-color: #1c1c1c; 
        --text-color: #CCCCCC;
    }
    /* Hide the overwritten chat message completely */
    .stChatMessage [data-testid="stMarkdownContainer"]:empty, 
    .stChatMessage [data-testid="stMarkdownContainer"]:has(:empty) {
        visibility: hidden;
        height: 0;
        margin: 0;
        padding: 0;
        border: none;
    }
    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Apply the theme and the hiding CSS
inject_final_css()

# --- State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.chat_history.append({"role": "assistant", "content": "Hello! I am PlotBot, your Q&A assistant. Please select a category below to get started."})

if "current_menu_key" not in st.session_state:
    st.session_state.current_menu_key = "MAIN"


st.title("CSV-Driven Q&A Bot 🏡")


# Helper function to display the current menu buttons
def display_menu(menu_dict):
    st.markdown("### Choose an Option:")
    
    cols = st.columns(3) 
    
    for i, (key, value) in enumerate(menu_dict.items()):
        
        button_key = f"btn_{st.session_state.current_menu_key}_{key}"
        
        if cols[i % 3].button(value, key=button_key):
            handle_user_selection(value)
            st.rerun() 


# Helper function to process user clicks
def handle_user_selection(value):
    
    CONFIRMATION_MESSAGE = "✅ Got it! Ready for your next question."
    # Unique character used to overwrite the message and trigger CSS hiding
    INVISIBLE_PLACEHOLDER = "" 

    # --- FIX APPLIED HERE: OVERWRITE LAST MESSAGE ---
    if st.session_state.chat_history and st.session_state.chat_history[-1]['content'] == CONFIRMATION_MESSAGE:
        # Overwrite the confirmation message with the empty placeholder
        st.session_state.chat_history[-1]['content'] = INVISIBLE_PLACEHOLDER


    # 1. Check if the selection is a main category (i.e., a subject)
    if value in st.session_state.main_menu.values():
        st.session_state.current_menu_key = value
        
    # 2. The selection is a specific question
    else:
        # Log the question and answer from the Assistant's perspective
        st.session_state.chat_history.append({"role": "assistant", "content": f"**Question:** {value}"})
        
        answer = get_fixed_answer(value)
        
        st.session_state.chat_history.append({"role": "assistant", "content": f"**Answer:** {answer}"})
        
        # After answering, return to the main menu
        st.session_state.current_menu_key = "MAIN"
        
        # Add the confirmation message (which will be overwritten on next click)
        st.session_state.chat_history.append({"role": "assistant", "content": CONFIRMATION_MESSAGE})


# 4. Display Chat History
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# 5. Menu Display Logic
if st.session_state.main_menu:
    if st.session_state.current_menu_key == "MAIN":
        display_menu(st.session_state.main_menu)
    else:
        # We are in a sub-menu
        menu_to_display = st.session_state.sub_menus.get(st.session_state.current_menu_key, {})
        
        # Display the "Go Back" button first
        back_button_key = f"back_btn_{st.session_state.current_menu_key}"
        if st.button("⬅️ Go Back to Main Menu", key=back_button_key):
            st.session_state.current_menu_key = "MAIN"
            st.rerun()
            
        display_menu(menu_to_display)
