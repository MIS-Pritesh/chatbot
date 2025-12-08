import streamlit as st
from collections import OrderedDict

# ======================================================================
# 1. DATA AND KNOWLEDGE BASE
# ======================================================================

# Simulate your database/backend data
PLOT_DATA = {
    '101': {'status': 'SOLD', 'size': 1200, 'price': '₹45,00,000'},
    '105': {'status': 'AVAILABLE', 'size': 1500, 'price': '₹56,00,000'},
    '115': {'status': 'HOLD', 'size': 900, 'price': '₹34,00,000'},
    '200': {'status': 'AVAILABLE', 'size': 1800, 'price': '₹65,00,000'},
    # Add all your plots here...
}

# --- MENU STRUCTURE MODIFIED ---
# "Plot Status & Details" category will now lead to the input box.

MAIN_MENU = OrderedDict([
    ("1", "Plot Status Lookup (Enter Plot Number)"), # Changed label
    ("2", "Legal & Financing Questions"),
    ("3", "General Project & Amenities"),
])

SUB_MENUS = {
    # This sub-menu is now just a placeholder/trigger for the text input
    "Plot Status Lookup (Enter Plot Number)": OrderedDict([
        ("ACTION_INPUT", "Enter Plot Number"), # NEW: Special action key
    ]),
    
    # Other sub-menus remain the same for fixed Q&A
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
# 2. ANSWER RETRIEVAL LOGIC (Updated to handle dynamic lookup)
# ======================================================================

def get_plot_details(plot_number):
    """Retrieves dynamic plot details based on the user input number."""
    info = PLOT_DATA.get(plot_number)
    
    if info:
        return (
            f"### Details for Plot {plot_number}:"
            f"\n\n**Status:** **{info['status']}**"
            f"\n**Size:** **{info['size']} sq. ft.**"
            f"\n**Price (All-inclusive):** **{info['price']}**"
        )
    return f"Plot **{plot_number}** not found. Please check your plot number and try again."


def get_fixed_answer(question):
    """Retrieves fixed answers for legal/amenities questions."""
    
    if "RERA registered" in question:
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

# --- State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.chat_history.append({"role": "assistant", "content": "Hello! I am PlotBot, your assistant. Please select a category below to get started."})

if "current_menu_key" not in st.session_state:
    st.session_state.current_menu_key = "MAIN"

if "awaiting_plot_number" not in st.session_state:
    st.session_state.awaiting_plot_number = False

st.title("Plot Management Q&A Bot 🏡")
st.sidebar.header("Navigation")

# Helper function to display the current menu buttons
def display_menu(menu_dict):
    st.markdown("### Choose an Option:")
    
    # Layout buttons in columns for better appearance
    cols = st.columns(3) 
    
    for i, (key, value) in enumerate(menu_dict.items()):
        # Use a unique key for each button and pass the menu action
        button_key = f"btn_{st.session_state.current_menu_key}_{key}"
        
        # We need to handle the button logic slightly differently if we use columns
        if cols[i % 3].button(value, key=button_key):
            handle_user_selection(key, value)
            st.rerun() 

# Helper function to process user clicks
def handle_user_selection(key, value):
    st.session_state.chat_history.append({"role": "user", "content": f"Selected: {value}"})
    
    # 1. Check if the selection is the special input action
    if key == "ACTION_INPUT":
        # Set the state to await the plot number
        st.session_state.awaiting_plot_number = True
        st.session_state.chat_history.append({"role": "assistant", "content": "Please enter the plot number (e.g., 101, 115) in the box below and hit Enter."})
        return

    # 2. Check if the selection is a main category
    if st.session_state.current_menu_key == "MAIN":
        st.session_state.current_menu_key = value
        
    # 3. Handle fixed answers (Legal/Amenities)
    else:
        # Retrieve the fixed answer
        answer = get_fixed_answer(value)
        st.session_state.chat_history.append({"role": "assistant", "content": f"**Question:** {value}\n\n**Answer:** {answer}"})
        # After answering, return to the main menu
        st.session_state.current_menu_key = "MAIN"
        st.session_state.chat_history.append({"role": "assistant", "content": "Answer provided. Please choose a new category from the main menu."})


# ======================================================================
# ... Sections 1, 2, and 3 (Data, Logic, and State Initialization) remain the same ...
# ... Place the revised code below after Section 3's state initialization ...
# ======================================================================


# 4. Display Chat History
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ----------------------------------------------------------------------
# 5. DYNAMIC PLOT NUMBER INPUT HANDLER (REVISED)
# ----------------------------------------------------------------------

# Check if the bot is currently waiting for the user to enter a plot number
if st.session_state.awaiting_plot_number:
    
    # 5a. Render the input field right after the chat history
    plot_input = st.text_input("Enter Plot Number (e.g., 101, 115):", key="plot_number_input_field")
    
    # 5b. Process the submission if the user enters text and hits Enter
    if plot_input:
        
        # Log the user's input
        st.session_state.chat_history.append({"role": "user", "content": f"Plot number entered: **{plot_input}**"})
        
        # Get the dynamic details
        details = get_plot_details(plot_input)
        
        # Display the answer
        st.session_state.chat_history.append({"role": "assistant", "content": details})
        
        # Reset the state and return to the main menu
        st.session_state.awaiting_plot_number = False
        st.session_state.current_menu_key = "MAIN"
        st.session_state.chat_history.append({"role": "assistant", "content": "Plot details provided. Please select a new action from the menu below."})
        
        # IMPORTANT: Rerun the app to clear the input box and show the main menu
        st.rerun()

# ----------------------------------------------------------------------
# 6. MENU DISPLAY LOGIC (REVISED)
# ----------------------------------------------------------------------

# Only display the menu if the bot is NOT waiting for plot input
if not st.session_state.awaiting_plot_number:
    
    # Check if we are at the main menu level
    if st.session_state.current_menu_key == "MAIN":
        
        # Display the main categories
        display_menu(MAIN_MENU)
        
    # Check if we are in a sub-menu level
    else:
        
        # Display the "Go Back" button
        back_button_key = f"back_btn_{st.session_state.current_menu_key}"
        if st.button("⬅️ Go Back to Main Menu", key=back_button_key):
            st.session_state.current_menu_key = "MAIN"
            st.rerun()

        menu_to_display = SUB_MENUS.get(st.session_state.current_menu_key, {})

        # Handle Plot Status Lookup trigger immediately
        if st.session_state.current_menu_key == "Plot Status Lookup (Enter Plot Number)":
            # Set the state to await input and rerun to show the input box
            st.session_state.awaiting_plot_number = True
            st.session_state.current_menu_key = "MAIN" # Return menu state to main
            
            # Log the message telling the user to enter the number
            st.session_state.chat_history.append({"role": "assistant", "content": "Please enter the plot number (e.g., 101, 115) in the box below and hit Enter."})
            st.rerun()
            
        else:
            # Display buttons for other sub-menus (Legal/Amenities)
            display_menu(menu_to_display)
            
st.sidebar.markdown("---")
st.sidebar.caption("This PlotBot runs on Streamlit's free tier, using fixed-rule logic and dynamic input handling.")
st.sidebar.markdown("---")
st.sidebar.caption("This PlotBot runs on Streamlit's free tier, using fixed-rule logic and dynamic input handling.")
