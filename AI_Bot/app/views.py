# views.py

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import json
import google.generativeai as genai

# Configure the Gemini API client once using the API key from settings.py
# This configuration is crucial for the bot to work.
genai.configure(api_key=settings.GEMINI_API_KEY)

# Use a global variable to maintain conversation context (chat history)
# The 'gemini-2.5-flash' model is fast and powerful for general and coding tasks.
model = genai.GenerativeModel('gemini-2.5-flash')


def chatpage(request):
    """Renders the main chat interface template."""
    return render(request, 'chatpage.html')


def get_ai_response(request):
    """Handles the user's message, sends it to the AI, and returns the response."""
    if request.method == 'POST':
        try:
            # 1. Parse the incoming JSON data from the frontend
            data = json.loads(request.body)
            user_input = data.get('user_input', '').strip()

            if not user_input:
                return JsonResponse({"reply": "Please enter a message."}, status=400)

            # --- 🚨 THE KEY FIX: Session-based History Management ---
            
            # 2. Retrieve history from the Django session (or start fresh)
            # The history is stored as a list of Content objects.
            chat_history_data = request.session.get('chat_history', [])

            # 3. Start a NEW chat session, injecting the history
            # The model variable is defined globally and is reusable.
            chat_session = model.start_chat(history=chat_history_data)

            # 4. Send the message and get the response
            # The chat_session automatically sends the user_input and all previous history.
            response = chat_session.send_message(user_input)
            
            # 5. Update and Save History back to the Django session
            # This fetches the full, updated history from the chat session object.
            request.session['chat_history'] = chat_session.get_history() 

            # 6. Extract the AI's text response
            ai_reply = response.text

            # 7. Return the AI's reply as a JSON response to the frontend
            return JsonResponse({"reply": ai_reply})

        except Exception as e:
            # Log the full error to your Render logs for debugging
            print(f"AI API Error: {e}") 
            # Return the specific error message to the frontend
            return JsonResponse({"reply": "Error: Could not connect to the AI. Please check the server."}, status=500)
    
    # Handle GET requests (e.g., if a user navigates directly to the URL)
    return JsonResponse({"reply": "Method not allowed"}, status=405)