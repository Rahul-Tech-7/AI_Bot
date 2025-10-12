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
# This starts a new chat session, which automatically keeps the message history.
global_chat_session = model.start_chat(history=[])

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

            # 2. Send the message to the AI and wait for the reply
            # The global_chat_session sends the user_input and all previous history.
            response = global_chat_session.send_message(user_input)
            
            # 3. Extract the AI's text response
            ai_reply = response.text

            # 4. Return the AI's reply as a JSON response to the frontend
            return JsonResponse({"reply": ai_reply})

        except Exception as e:
            print(f"AI API Error: {e}")
            return JsonResponse({"reply": "Sorry, I ran into an error. Please try again."}, status=500)
    
    # Handle GET requests (e.g., if a user navigates directly to the URL)
    return JsonResponse({"reply": "Method not allowed"}, status=405)