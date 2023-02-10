from django.shortcuts import render
from django.http import JsonResponse
import os
import re
import datetime

from .models import Question

import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

default_model_engine = "text-davinci-003"
default_max_tokens = 2048
default_log_base = "logs/"
default_context = """The following is a conversation with an AI assistant. The assistant has a profound knowledge of LinkedIn Marketing Solutions.
She has read all articles in the following site: https://www.linkedin.com/help/lms
Not only that, but she also knows everything from this site: https://business.linkedin.com/marketing-solutions
The assistant loves Linkedin and believes that Linkedin is the best for B2B marketing.
AI: How can I help today?
"""
tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)

code_gen_context = """
The following is a conversation with an AI code generator. The AI code generator always returns code quote with ```
THe AI code generator is concise without the need to setup ACCESS_TOKEN and HTTP headers.
The AI code generator always show the resource url.
The AI code generator has a profound knowledge of LinkedIn Marketing API from the following sites:
https://learn.microsoft.com/en-us/linkedin/marketing/
The AI code generator can find campaign schema from the following page:
https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaigns?view=li-lms-2023-02&tabs=http
`startTime` is default to {}, `endTime` default to a week from `startTime`.
`campaignType` is default to `SPONSORED_UPDATES`

AI: What code do you like to create?
""".format(tomorrow)

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
    is_code = "code" in prompt.lower()
    completions = {'choices':[{'text': "Sorry, I am having trouble understanding. Can you please repeat your question?"}]}
    try:
        if not os.path.exists(default_log_base + session_key + ".txt"):
            # pre_history = code_gen_context if is_code else default_context
            with open(default_log_base + session_key + ".txt", "w+") as f:
                f.write("")

        with open(default_log_base + session_key + ".txt", "r+") as f:
            pre_load_context = f.read()
        pre_load_context = "\n".join(pre_load_context.splitlines()[-6:]) + "\n"
        if is_code:
            prompt = code_gen_context + pre_load_context + history + "\nAI: "
            prompt = (f"{prompt}")
            completions = openai.Completion.create(
                engine="code-davinci-002",
                prompt=prompt,
                max_tokens=4000,
                n=1,
                stop=['Human', 'AI'],
                temperature=0.4,
                presence_penalty = 0,
                frequency_penalty = 0,
                user = session_key,
            )
        else:
            prompt = default_context + pre_load_context + history + "\nAI: "
            prompt = (f"{prompt}")
            completions = openai.Completion.create(
                engine=model_engine,
                prompt=prompt,
                max_tokens=default_max_tokens,
                n=1,
                stop=['Human', 'AI'],
                temperature=0.4,
                presence_penalty = 1,
                user = session_key,
            )

        message = completions.choices[0].text
        message = message.strip()
        data = {'answer':  message}
        print(message)
        if is_code:
            rendered_message = re.sub("```", "<pre><code>", message, 1)
            rendered_message = re.sub("```", "</code></pre>", rendered_message, 1)
            data= {'answer':  rendered_message}
        history = history + "AI: " + message + "\n"
        log(session_key, history)
    except Exception as e:
        print(e)
        data = {'answer': "Sorry, I am having trouble understanding. Can you please repeat your question?"}

    return JsonResponse(data)

def log(session_key, history):
    default_log_base = "logs/"
    with open(default_log_base + session_key + ".txt", "a+") as f:
        f.write(history)
