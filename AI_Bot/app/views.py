from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import json
# REMOVE: import google.generativeai as genai
# USE NEW SDK:
from google import genai 
from django.views.decorators.csrf import csrf_exempt # IMPORTANT: keep this!

# Configure the Gemini API client once using the API key from settings.py
# The new SDK uses a client object.
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Use a global variable to maintain conversation context (chat history)
# The 'gemini-2.5-flash' model is fast and powerful for general and coding tasks.

# NEW WAY to start a chat session using the client.
global_chat_session = client.chats.create(model='gemini-2.5-flash')


def chatpage(request):
    """Renders the main chat interface template."""
    return render(request, 'chatpage.html')


@csrf_exempt # Ensure this decorator is still here!
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
            # You may want to log the specific error `e` on Render to debug
            return JsonResponse({"reply": "Sorry, I ran into an error. Please try again."}, status=500)
    
    # Handle GET requests (optional)
    return JsonResponse({"reply": "This endpoint requires a POST request."}, status=405)