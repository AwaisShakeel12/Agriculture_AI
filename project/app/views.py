from django.shortcuts import render
from .Lang import graph

from django.shortcuts import render
from .Lang import graph

# def home(request):
#     ai_response = ""

#     if request.method == 'POST':
#         user_msg = request.POST.get('user_msg', '')

#         # Get the response from LangGraph
#         initial_input = {'messages': user_msg}
#         thread = {'configurable': {'thread_id': '1'}}

#         for event in graph.stream(initial_input, thread, stream_mode='values'):
#             ai_response = event['messages'][-1]  # Get the AI response

#         return render(request, 'index.html', {'user_msg': user_msg, 'ai_response': ai_response})

#     return render(request, 'index.html')




def home(request):
    # Use a single conversation history
    if 'conversation' not in request.session:
        request.session['conversation'] = []

    conversation = request.session['conversation']

    if request.method == 'POST':
        user_msg = request.POST.get('user_msg', '')

        conversation.append({'sender': 'User', 'message': user_msg})

        initial_input = {'messages': [user_msg]}  # Send user input to AI
        thread_data = {'configurable': {'thread_id': '4'}}  # Hardcoded thread
        
        response = graph.stream(initial_input, thread_data, stream_mode='values')

        ai_response = ""
        
        for event in response:
            message = event['messages'][-1]
            if hasattr(message, 'additional_kwargs') and 'tool_calls' in message.additional_kwargs:
                continue
            ai_response = message.content

        if ai_response:
            conversation.append({'sender': 'AI', 'message': ai_response})

        request.session['conversation'] = conversation
        request.session.modified = True  # Ensure session updates

    return render(request, 'home.html', {'conversation': conversation})