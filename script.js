// script.js
// --- CONFIGURATION ---
// PASTE YOUR ACTUAL VERCEL DOMAIN HERE (e.g., https://chatbot-e56m.vercel.app)
const API_BASE_URL = 'https://chatbot-hnls.vercel.app'; // <--- **THIS MUST BE YOUR LIVE VERCEL LINK**

// ... (rest of the code remains the same)

// --- STATE MANAGEMENT ---
let currentSubject = null; 

const chatHistory = document.getElementById('chatHistory');
const optionsContainer = document.getElementById('optionsContainer');

// --- HELPER FUNCTIONS ---

// Adds a new message to the chat history
function addMessage(role, content) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    msgDiv.innerHTML = content;
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight; // Scroll to bottom
}

// Loads buttons dynamically
function loadOptions(title, options, clickHandler, type) {
    optionsContainer.innerHTML = `<h3>${title}</h3>`;
    options.forEach(option => {
        const button = document.createElement('button');
        button.textContent = option;
        // Use encodeURIComponent to handle spaces and special characters in URLs
        button.onclick = () => clickHandler(encodeURIComponent(option), option); 
        optionsContainer.appendChild(button);
    });

    // Add back button for question menu
    if (type === 'questions') {
        const backButton = document.createElement('button');
        backButton.textContent = "⬅️ Go Back to Main Menu";
        backButton.onclick = () => loadMainMenu();
        optionsContainer.appendChild(backButton);
    }
}

// --- API FETCH LOGIC ---

// 1. Loads the main subject menu
async function loadMainMenu() {
    currentSubject = null;
    const url = `${API_BASE_URL}/menu`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.error) throw new Error(data.error);

        loadOptions('Choose an Option:', data, loadQuestionMenu, 'menu');
    } catch (error) {
        addMessage('bot', `Error loading menu: ${error.message}`);
    }
}

// 2. Loads the questions for a selected subject
async function loadQuestionMenu(encodedSubject, subjectText) {
    currentSubject = subjectText;
    // The subject is already encoded when passed from the button click
    const url = `${API_BASE_URL}/questions/${encodedSubject}`; 
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.error) throw new Error(data.error);
        
        loadOptions(`Questions for: ${subjectText}`, data, getAnswer, 'questions');
    } catch (error) {
        addMessage('bot', `Error loading questions: ${error.message}`);
        loadMainMenu(); // Go back on error
    }
}

// 3. Gets the answer for a selected question
async function getAnswer(encodedQuestion, questionText) {
    // Add the question to the chat history
    addMessage('bot', `<strong>Question:</strong> ${questionText}`); 
    
    const url = `${API_BASE_URL}/answer?question=${encodedQuestion}`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();

        // Display the answer
        addMessage('bot', `<strong>Answer:</strong> ${data.answer}`);
        
        // Show confirmation and return to main menu
        addMessage('bot', `✅ Got it! Ready for your next question.`); 
        loadMainMenu();
    } catch (error) {
        addMessage('bot', `Error fetching answer: ${error.message}`);
        loadMainMenu();
    }
}

// Start the application by loading the main menu
document.addEventListener('DOMContentLoaded', loadMainMenu);
