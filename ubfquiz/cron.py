from .models import *
import datetime

def auto_sumbit_task():
        
        quiztakers = QuizTaker.objects.filter(completed=False)

        for i in quiztakers:
            if i.quiz.live==False:
                if datetime.datetime.now()>i.starttime+i.quiz.duration):
                    quiztaker = QuizTaker.objects.get(id=i.id)
                    quiztaker.complete=True
                    quiztaker.date_finished=datetime.now()
                    correct_answers = 0

                    for users_answer in models.UsersAnswer.objects.filter(quiz_taker=quiztaker):
                        answer = models.Answer.objects.get(question=users_answer.question, is_correct=True)
                        if users_answer.answer == answer:
                            correct_answers += 1

                    quiztaker.score = int(correct_answers / quiztaker.quiz.question_set.count() * 100)

                    aggregate = models.QuizTaker.objects.filter(quiz_id =quiztaker.quiz.id,score__gt=quiztaker.score).aggregate(ranking=Count('score'))
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
                    if datetime.datetime.now()>(lastslot.start_datetime+quiztaker.quiz.duration):
                        quiztaker = QuizTaker.objects.get(id=i.id)
                        quiztaker.complete=True
                        quiztaker.date_finished=datetime.now()
                        correct_answers = 0

                        for users_answer in models.UsersAnswer.objects.filter(quiz_taker=quiztaker):
                            answer = models.Answer.objects.get(question=users_answer.question, is_correct=True)
                            if users_answer.answer == answer:
                                correct_answers += 1

                        quiztaker.score = int(correct_answers / quiztaker.quiz.question_set.count() * 100)

                        aggregate = models.QuizTaker.objects.filter(quiz_id =quiztaker.quiz.id,score__gt=quiztaker.score).aggregate(ranking=Count('score'))
                        quiztaker.quiz_day_rank = int(aggregate['ranking'] + 1)
                        quiztaker.save()
                else:
                    if datetime.datetime.now()>(slot.start_datetime+i.quiz.duration):
                        quiztaker = QuizTaker.objects.get(id=i.id)
                        quiztaker.complete=True
                        quiztaker.date_finished=datetime.now()
                        correct_answers = 0

                        for users_answer in models.UsersAnswer.objects.filter(quiz_taker=quiztaker):
                            answer = models.Answer.objects.get(question=users_answer.question, is_correct=True)
                            if users_answer.answer == answer:
                                correct_answers += 1

                        quiztaker.score = int(correct_answers / quiztaker.quiz.question_set.count() * 100)

                        aggregate = models.QuizTaker.objects.filter(quiz_id =quiztaker.quiz.id,score__gt=quiztaker.score).aggregate(ranking=Count('score'))
                        quiztaker.quiz_day_rank = int(aggregate['ranking'] + 1)
                        quiztaker.save()

def temp_task():
    Tester.objects.create(name="testing")