from django.db import models

class Question(models.Model):
    question_text = models.CharField(max_length=511)
    pub_date = models.DateTimeField('date published')
    url = models.URLField(max_length=1023)

# Create your models here.
