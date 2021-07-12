# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery import shared_task
# from demoapp.models import Widget
#from quiz import models
from django.db.models import Q, Count
from .models import *
import time 
import datetime
from django.utils import timezone


@shared_task
def auto_submit_task():
        
    quiztakers = QuizTaker.objects.filter(completed=False)
    #now = timezone.now()
    #now= now + datetime.timedelta(hours=5,minutes=30)
    #print(now)
    for i in quiztakers:
        now = timezone.now()
        #now = now + datetime.timedelta(hours=5,minutes=30)
        #print(now)
        #print(datetime.datetime.now())
        if i.quiz.live==False:
            print(i.starttime+i.quiz.duration)
            if now>(i.starttime+i.quiz.duration):
                quiztaker = QuizTaker.objects.get(id=i.id)
                quiztaker.complete=1
                quiztaker.date_finished=datetime.datetime.now()
                correct_answers = 0

                for users_answer in UsersAnswer.objects.filter(quiz_taker=quiztaker):
                    answer = Answer.objects.get(question=users_answer.question, is_correct=True)
                    if users_answer.answer == answer:
                        correct_answers += 1

                quiztaker.score = int(correct_answers / quiztaker.quiz.question_set.count() * 100)

                aggregate = QuizTaker.objects.filter(quiz_id =quiztaker.quiz.id,score__gt=quiztaker.score).aggregate(ranking=Count('score'))
                quiztaker.quiz_day_rank = int(aggregate['ranking'] + 1)
                quiztaker.save()

        if i.quiz.live == True:
            slots = QuizSlot.objects.filter(quiz=i.quiz)
            temp=False
            slot=None
            lastslot=slots[0]
            for j in slots:
                if j.start_datetime>lastslot.start_datetime:
                    lastslot=j
                if j.start_datetime>=datetime.datetime.now():
                    temp=True
                    slot=j
                    break 
            if temp == False:
                if now>(lastslot.start_datetime+quiztaker.quiz.duration):
                    quiztaker = QuizTaker.objects.get(id=i.id)
                    quiztaker.complete=True
                    quiztaker.date_finished=datetime.datetime.now()                      
                    correct_answers = 0

                    for users_answer in UsersAnswer.objects.filter(quiz_taker=quiztaker):
                        answer = Answer.objects.get(question=users_answer.question, is_correct=True)
                        if users_answer.answer == answer:
                            correct_answers += 1

                    quiztaker.score = int(correct_answers / quiztaker.quiz.question_set.count() * 100)

                    aggregate = QuizTaker.objects.filter(quiz_id =quiztaker.quiz.id,score__gt=quiztaker.score).aggregate(ranking=Count('score'))
                    quiztaker.quiz_day_rank = int(aggregate['ranking'] + 1)
                    quiztaker.save()
            else:
                if now>(slot.start_datetime+i.quiz.duration):
                    quiztaker = QuizTaker.objects.get(id=i.id)
                    quiztaker.complete=True
                    quiztaker.date_finished=datetime.datetime.now()
                    correct_answers = 0
                    for users_answer in UsersAnswer.objects.filter(quiz_taker=quiztaker):
                        answer = Answer.objects.get(question=users_answer.question, is_correct=True)
                        if users_answer.answer == answer:
                            correct_answers += 1

                    quiztaker.score = int(correct_answers / quiztaker.quiz.question_set.count() * 100)

                    aggregate = QuizTaker.objects.filter(quiz_id =quiztaker.quiz.id,score__gt=quiztaker.score).aggregate(ranking=Count('score'))
                    quiztaker.quiz_day_rank = int(aggregate['ranking'] + 1)
                    quiztaker.save()
    return True

@shared_task
def quiz_rollout():

    quizzes = Quiz.objects.filter(roll_out=False)

    for quiz in quizzes:
        now = timezone.now()
        
        if now>=quiz.rollout_date:

            obj = Quiz.objects.get(id=quiz.id)

            obj.roll_out =True
            obj.save()
    
    return True
