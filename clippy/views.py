from django.shortcuts import render
from django.http import JsonResponse

from .models import Question

import openai
openai.api_key = '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'
def index(request):
    question_list = Question.objects.order_by('pub_date')
    context = {
        'question_list': question_list
    }
    return render(request, 'index.html', context)

def chat(request):
    prompt = request.POST.get("message")
    model_engine = "text-davinci-003"
    prompt = (f"{prompt}")
    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = completions.choices[0].text
    data= {'answer':  message.strip()}
    return JsonResponse(data)
