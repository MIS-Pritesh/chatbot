import streamlit as st
import pandas as pd
import os
from collections import OrderedDict

# ======================================================================
# 1. DATA LOADING AND PROCESSING
# ======================================================================

# Define the expected filename
CSV_FILE_PATH = "data.csv"

def load_and_structure_data(file_path):
    """
    Loads data from CSV, structures it into an organized dictionary
    for menu display, and returns the main subjects and sub-menus.
    """
    if not os.path.exists(file_path):
        st.error(f"FATAL ERROR: Data file '{file_path}' not found in the deployment directory.")
        return OrderedDict(), {}

    try:
        # Load the CSV file
        df = pd.read_csv(file_path)
        
        # Ensure required columns exist
        REQUIRED_COLS = ['subject', 'question', 'answer']
        if not all(col in df.columns for col in REQUIRED_COLS):
            st.error(f"FATAL ERROR: CSV must contain the columns: {', '.join(REQUIRED_COLS)}")
            return OrderedDict(), {}
        
        # Use OrderedDict to maintain the order of main subjects based on first appearance
        main_menu = OrderedDict() 
        sub_menus = {}

        # Group data by the 'subject' column
        grouped_data = df.groupby('subject')
        
        for subject, group in grouped_data:
            # 1. Build the Main Menu (subjects)
            # Find a unique key for the main menu, e.g., '1', '2', etc.
            key = str(len(main_menu) + 1)
            main_menu[key] = subject
            
            # 2. Build the Sub-Menu (questions for that subject)
            sub_menu_questions = OrderedDict()
            for i, row in enumerate(group.itertuples()):
                q_key = str(i + 1)
                sub_menu_questions[q_key] = row.question
            
            sub_menus[subject] = sub_menu_questions

        # 3. Store the full Q&A dataframe for quick answer lookup
        # Use cache=True for better performance, but Streamlit handles caching for load_data() 
        st.session_state.qa_data = df
        
        return main_menu, sub_menus

    except Exception as e:
        st.error(f"FATAL ERROR: Failed to load or process CSV data. Check file permissions or formatting. Error: {e}")
        return OrderedDict(), {}

# Load data only once at the start of the session
if 'main_menu' not in st.session_state:
    st.session_state.main_menu, st.session_state.sub_menus = load_and_structure_data(CSV_FILE_PATH)


# ======================================================================
# 2. ANSWER RETRIEVAL LOGIC
# ======================================================================

def get_fixed_answer(question):
    """Retrieves the answer by searching the loaded DataFrame."""
    if 'qa_data' not in st.session_state:
        return "System error: Data not loaded."
        
    try:
        # Search the DataFrame for the matching question
        answer_row = st.session_state.qa_data[st.session_state.qa_data['question'] == question]
        
        if not answer_row.empty:
            # Return the first matching answer
            return answer_row.iloc[0]['answer']
        
        return "I'm sorry, I could not find a specific answer for that question in my database."
    except Exception as e:
        return f"An internal error occurred during lookup: {e}"


# ======================================================================
# 3. STREAMLIT APPLICATION SETUP AND UI
# ======================================================================

# --- State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.chat_history.append({"role": "assistant", "content": "Hello! I am PlotBot, your Q&A assistant. Please select a category below to get started."})

if "current_menu_key" not in st.session_state:
    st.session_state.current_menu_key = "MAIN"

st.title("CSV-Driven Q&A Bot 🏡")
st.sidebar.header("Data Source")
st.sidebar.info(f"Loaded {len(st.session_state.main_menu)} main subjects from **{CSV_FILE_PATH}**.")


# Helper function to display the current menu buttons
def display_menu(menu_dict):
    st.markdown("### Choose an Option:")
    
    # Use columns for a clean button layout (up to 3 buttons per row)
    cols = st.columns(3) 
    
    for i, (key, value) in enumerate(menu_dict.items()):
        
        button_key = f"btn_{st.session_state.current_menu_key}_{key}"
        
        if cols[i % 3].button(value, key=button_key):
            handle_user_selection(value)
            st.rerun() 


# Helper function to process user clicks
def handle_user_selection(value):
    # 1. Log the User's question/action
    st.session_state.chat_history.append({"role": "user", "content": f"Selected: {value}"})
    
    # 2. Check if the selection is a main category (i.e., a subject)
    if value in st.session_state.main_menu.values():
        # Set state to the subject text to display its sub-menu
        st.session_state.current_menu_key = value
        
    # 3. The selection is a specific question
    else:
        # Retrieve the fixed answer using the full question text
        answer = get_fixed_answer(value)
        
        st.session_state.chat_history.append({"role": "assistant", "content": f"**Question:** {value}\n\n**Answer:** {answer}"})
        
        # After answering, return to the main menu
        st.session_state.current_menu_key = "MAIN"
        st.session_state.chat_history.append({"role": "assistant", "content": "Answer provided. Please choose a new category from the main menu."})


# 4. Display Chat History
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# 5. Menu Display Logic

if st.session_state.current_menu_key == "MAIN":
    # Show the main categories (subjects from CSV)
    display_menu(st.session_state.main_menu)
else:
    # We are in a sub-menu (questions for a specific subject)
    
    # Get the dictionary of questions for the current subject key
    menu_to_display = st.session_state.sub_menus.get(st.session_state.current_menu_key, {})
    
    # Display the "Go Back" button first
    back_button_key = f"back_btn_{st.session_state.current_menu_key}"
    if st.button("⬅️ Go Back to Main Menu", key=back_button_key):
        st.session_state.current_menu_key = "MAIN"
        st.rerun()
        
    # Display the sub-menu options (questions)
    display_menu(menu_to_display)

st.sidebar.markdown("---")
st.sidebar.caption("This Q&A Bot is a 100% free solution powered by Python, Pandas, and Streamlit.")
