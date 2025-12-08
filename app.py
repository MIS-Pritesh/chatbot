import streamlit as st
import pandas as pd
import os
from collections import OrderedDict

# ======================================================================
# 1. DATA LOADING AND PROCESSING
# ======================================================================

# FIX APPLIED HERE: File name must match your GitHub file name exactly
CSV_FILE_NAME = "Data.csv" 

@st.cache_data
def load_and_structure_data(file_name):
    """
    Loads data from CSV, structures it into an organized dictionary
    for menu display, and returns the main subjects and sub-menus.
    Uses st.cache_data to run only once.
    """
    # --- Robust Path Finding ---
    # 1. Construct the absolute path by joining the script's directory with the filename.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)
    
    # Check one last time before raising the error
    if not os.path.exists(file_path):
        st.error(f"FATAL ERROR: Data file '{file_name}' not found. Please ensure the file is named **Data.csv** and is in the same directory as app.py.")
        return OrderedDict(), {}
    # ---------------------------
    
    try:
        df = pd.read_csv(file_path)
        
        REQUIRED_COLS = ['subject', 'question', 'answer']
        if not all(col in df.columns for col in REQUIRED_COLS):
            st.error(f"FATAL ERROR: CSV must contain the columns: {', '.join(REQUIRED_COLS)}")
            return OrderedDict(), {}
        
        main_menu = OrderedDict() 
        sub_menus = {}
        grouped_data = df.groupby('subject')
        
        for subject, group in grouped_data:
            # Build the Main Menu (subjects)
            key = str(len(main_menu) + 1)
            main_menu[key] = subject
            
            # Build the Sub-Menu (questions for that subject)
            sub_menu_questions = OrderedDict()
            for i, row in enumerate(group.itertuples()):
                q_key = str(i + 1)
                sub_menu_questions[q_key] = row.question
            
            sub_menus[subject] = sub_menu_questions

        return main_menu, sub_menus, df # Return the dataframe too

    except Exception as e:
        st.error(f"FATAL ERROR: Failed to load or process CSV data. Check file formatting. Error: {e}")
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
# 3. THEME INJECTION AND STREAMLIT SETUP
# ======================================================================

def inject_theme_css(theme):
    """Injects custom CSS based on the selected theme."""
    
    custom_themes = {
        "Classic Light": {
            "--primary-color": "#4CAF50",  # Green button/link color
            "--background-color": "#F0F2F6", # Very light grey background
            "--text-color": "#333333",
        },
        "Developer Dark": {
            "--primary-color": "#FF4B4B",  # Streamlit default red buttons
            "--background-color": "#1C1C1C", # Dark charcoal background
            "--text-color": "#CCCCCC",
        }
    }

    if theme == "Streamlit Default":
        st.markdown("<style></style>", unsafe_allow_html=True)
        return

    css_vars = custom_themes.get(theme, {})
    
    # Construct the CSS string
    css = ":root {\n"
    for var, color in css_vars.items():
        css += f"  {var}: {color};\n"
    css += "}\n"
    
    # Inject the CSS into the Streamlit app
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# --- Theme Selector Logic ---
# st.sidebar.header("App Settings")
# selected_theme = st.sidebar.selectbox(
#     "Select App Theme:",
#     ["Classic Light", "Developer Dark", "Streamlit Default"]
# )

# if 'app_theme' not in st.session_state or st.session_state.app_theme != selected_theme:
#     st.session_state.app_theme = selected_theme
#     st.rerun() # Rerun to apply new theme immediately

# # Apply the theme CSS
# inject_theme_css(st.session_state.app_theme)


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
    st.session_state.chat_history.append({"role": "user", "content": f"Selected: {value}"})
    
    # 1. Check if the selection is a main category (i.e., a subject)
    if value in st.session_state.main_menu.values():
        st.session_state.current_menu_key = value
        
    # 2. The selection is a specific question
    else:
        answer = get_fixed_answer(value)
        
        st.session_state.chat_history.append({"role": "assistant", "content": f"**Question:** {value}\n\n**Answer:** {answer}"})
        
        # After answering, return to the main menu
        st.session_state.current_menu_key = "MAIN"
        st.session_state.chat_history.append({"role": "assistant", "content": "📋 Ready for your next question."})


# 4. Display Chat History
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# 5. Menu Display Logic (only if data loaded)
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
