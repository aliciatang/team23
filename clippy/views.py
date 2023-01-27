from django.shortcuts import render
from django.http import JsonResponse

from .models import Question

def index(request):
    question_list = Question.objects.order_by('pub_date')
    context = {
        'question_list': question_list
    }
    return render(request, 'index.html', context)

def chat(request):
    data= {'answer': 'clippy says hi.'}
    return JsonResponse(data)

