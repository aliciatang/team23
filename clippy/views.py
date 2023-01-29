from django.shortcuts import render
from django.http import JsonResponse
import os

from .models import Question

import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
model_engine = "text-davinci-003"
context = """The following is a conversation with an AI assistant. The assistant has a profound knowledge of LinkedIn Marketing Solutions. She has read all articles in the following site: https://www.linkedin.com/help/lms
Not only that, but she also knows everything from this site: https://business.linkedin.com/marketing-solutions

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
    return JsonResponse(data)
