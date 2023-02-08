from django.shortcuts import render
from django.http import JsonResponse
import os

from .models import Question

import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
default_model_engine = "text-davinci-003"
context = """The following is a conversation with an AI assistant. The assistant has a profound knowledge of LinkedIn Marketing Solutions. She has read all articles in the following site: https://www.linkedin.com/help/lms and nothing else.
Not only that, but she also knows everything from this site: https://business.linkedin.com/marketing-solutions
The assistant loves Linkedin and believes that Linkedin is the best for B2B marketing.
The assistant also knows REST API for LMS from the following site: https://learn.microsoft.com/en-us/linkedin/marketing/

Human: Hello, who are you?
AI: I am an Linkedin AI powered by OpenAI. How can I help you today?
Human:
"""

def index(request):
    question_list = Question.objects.order_by('pub_date')
    context = {
        'question_list': question_list
    }
    return render(request, 'index.html', context)

def chat(request):
    prompt = request.POST.get("message")
    session_key = request.session.session_key
    history = "Human: " + prompt + "\n"
    model_engine = default_model_engine
    if "code" in prompt.lower():
        model_engine = "code-davinci-002"
    prompt = context + prompt + "\nAI: "
    prompt = (f"{prompt}")
    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=['Human', 'AI'],
        temperature=0.4,
    )

    message = completions.choices[0].text
    data= {'answer':  message.strip()}
    history = history + "AI: " + data['answer'] + "\n"
    log(session_key, history)

    return JsonResponse(data)

def log(session_key, history):
    base = "logs/"
    with open( base + session_key + ".txt", "w+") as f:
        f.write(history)
