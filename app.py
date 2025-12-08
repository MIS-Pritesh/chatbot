import streamlit as st
import re # We keep re, though not strictly needed for menu, it's good for potential extensions
from collections import OrderedDict # Use OrderedDict to maintain menu order

# ======================================================================
# 1. DATA AND KNOWLEDGE BASE (Your fixed Q&A Data)
# ======================================================================

# Simulate your database/backend data
PLOT_DATA = {
    '101': {'status': 'SOLD', 'size': 1200, 'price': '₹45,00,000'},
    '105': {'status': 'AVAILABLE', 'size': 1500, 'price': '₹56,00,000'},
    '115': {'status': 'HOLD', 'size': 900, 'price': '₹34,00,000'},
    # Add all your plots here...
}

# Use OrderedDict to ensure the menu options appear in the correct order
MAIN_MENU = OrderedDict([
    ("1", "Plot Status & Details"),
    ("2", "Legal & Financing Questions"),
    ("3", "General Project & Amenities"),
])

SUB_MENUS = {
    "Plot Status & Details": OrderedDict([
        ("1", "What is the status and price of Plot 101?"),
        ("2", "What is the status and price of Plot 105?"),
        ("3", "What is the status and price of Plot 115?"),
    ]),
    "Legal & Financing Questions": OrderedDict([
        ("1", "Is the project RERA registered? What is the ID?"),
        ("2", "Are bank loans available for this project?"),
        ("3", "What is the policy for booking cancellation/refund?"),
    ]),
    "General Project & Amenities": OrderedDict([
        ("1", "What are the key amenities provided in the project?"),
        ("2", "What is the distance to the nearest main road?"),
        ("3", "What is the expected possession date?"),
    ])
}

# ======================================================================
# 2. ANSWER RETRIEVAL LOGIC
# ======================================================================

def get_answer(question):
    """Retrieves the fixed answer based on the menu question."""
    
    # --- Check for specific Plot Data queries ---
    if "Plot 101" in question:
        info = PLOT_DATA.get('101', {})
        if info:
            return f"Plot **101** Status: **{info['status']}**. Size: **{info['size']} sq. ft.** Price: **{info['price']}**."
        return "Plot 101 details not found in the database."
        
    elif "Plot 105" in question:
        info = PLOT_DATA.get('105', {})
        if info:
            return f"Plot **105** Status: **{info['status']}**. Size: **{info['size']} sq. ft.** Price: **{info['price']}**."
        return "Plot 105 details not found in the database."
        
    elif "Plot 115" in question:
        info = PLOT_DATA.get('115', {})
        if info:
            return f"Plot **115** Status: **{info['status']}**. Size: **{info['size']} sq. ft.** Price: **{info['price']}**."
        return "Plot 115 details not found in the database."
        
    # --- Check for other fixed answers ---
    elif "RERA registered" in question:
        return "Yes, the project is fully RERA registered. RERA ID: **RERA/P/1234/5678**."
    elif "bank loans" in question:
        return "Bank loans are available from **HDFC, SBI, and ICICI** as the project is pre-approved."
    elif "cancellation/refund" in question:
        return "A full refund is provided if cancellation occurs within 7 days of booking, subject to administrative fees."
    elif "amenities" in question:
        return "Key amenities include a paved road network, 24/7 water supply, electricity, and a dedicated park area."
    elif "main road" in question:
        return "The site is located just **500 meters** from the main National Highway."
    elif "possession date" in question:
        return "The expected date of possession is **Q4 2026**."
        
    return "Error: Could not retrieve a specific answer for this question."

# ======================================================================
# 3. STREAMLIT APPLICATION SETUP
# ======================================================================

# Initialize chat history in Streamlit session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.chat_history.append({"role": "assistant", "content": "Hello! I am PlotBot, your assistant. Please select a category below to get started."})

# Initialize current menu state
if "current_menu_key" not in st.session_state:
    st.session_state.current_menu_key = "MAIN"

st.title("Plot Management Q&A Bot 🏡")
st.sidebar.header("Navigation")

# Helper function to display the current menu buttons
def display_menu(menu_dict):
    st.markdown("### Choose an Option:")
    cols = st.columns(len(menu_dict))
    
    for i, (key, value) in enumerate(menu_dict.items()):
        # Use a unique key for each button and pass the menu action
        button_key = f"btn_{st.session_state.current_menu_key}_{key}"
        if cols[i].button(value, key=button_key):
            handle_user_selection(key, value)
            st.rerun() # Rerun the app to update the state and chat history

# Helper function to process user clicks
def handle_user_selection(key, value):
    # 1. Log the User's question/action
    st.session_state.chat_history.append({"role": "user", "content": f"Selected: {value}"})

    # 2. Check if the selection is a main category
    if st.session_state.current_menu_key == "MAIN":
        st.session_state.current_menu_key = value
        
    # 3. Check if the selection is a specific question
    elif value in [item for sub in SUB_MENUS.values() for item in sub.values()]:
        # Retrieve the fixed answer
        answer = get_answer(value)
        st.session_state.chat_history.append({"role": "assistant", "content": f"**Question:** {value}\n\n**Answer:** {answer}"})
        # After answering, return to the main menu for simplicity
        st.session_state.current_menu_key = "MAIN"
        st.session_state.chat_history.append({"role": "assistant", "content": "Answer provided. Please choose a new category from the main menu."})

# 4. Handle Menu Display
# Display chat history first
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Determine which menu to show
if st.session_state.current_menu_key == "MAIN":
    # Show the main categories
    display_menu(MAIN_MENU)
else:
    # Show the sub-menu items
    menu_to_display = SUB_MENUS.get(st.session_state.current_menu_key, {})
    
    # Add the "Go Back" button dynamically
    back_button_key = f"back_btn_{st.session_state.current_menu_key}"
    if st.button("⬅️ Go Back to Main Menu", key=back_button_key):
        st.session_state.current_menu_key = "MAIN"
        st.rerun()

    # Display the sub-menu options
    display_menu(menu_to_display)

st.sidebar.markdown("---")
st.sidebar.caption("This PlotBot runs entirely on Streamlit's free tier, using fixed-rule logic for accurate, zero-cost Q&A.")
