from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from datetime import timedelta,datetime

#from quiz.tasks import EndQuiz

class Quiz(models.Model):
	name = models.CharField(max_length=100)
	description = models.CharField(max_length=70)
	image = models.ImageField()
	slug = models.SlugField(blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	price = models.PositiveSmallIntegerField()
	duration = models.DurationField(default=timedelta(hours=2))
	live = models.BooleanField(default=False)
	roll_out = models.BooleanField(default=False)
	rollout_date=models.DateTimeField(blank=True,null=True)
	answerkey=models.FileField(blank=True,null=True)

	class Meta:
		ordering = ['timestamp',]
		verbose_name_plural = "Quizzes"

	def __str__(self):
		return self.name

class QuizSlot(models.Model):
	quiz = models.ForeignKey('ubfquiz.Quiz', on_delete=models.CASCADE)
	start_datetime = models.DateTimeField()

	class Meta:
		verbose_name_plural = "Quiz Slots"

	# def __str__(self):
	# 	return self.quiz

class Question(models.Model):
	quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
	label = models.CharField(max_length=100)
	order = models.IntegerField(default=0)

	def __str__(self):
		return self.label


class Answer(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	label = models.CharField(max_length=100)
	is_correct = models.BooleanField(default=False)

	def __str__(self):
		return self.label


class QuizTaker(models.Model):
	student = models.ForeignKey('student.Student', on_delete=models.CASCADE)
	quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
	score = models.IntegerField(default=0)
	completed = models.BooleanField(default=False)
	date_finished = models.DateTimeField(null=True, blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	quiz_day_rank = models.PositiveIntegerField(null=True, blank=True)
	starttime = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.student.email


class UsersAnswer(models.Model):
	quiz_taker = models.ForeignKey(QuizTaker, on_delete=models.CASCADE)
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True)

	def __str__(self):
		return self.question.label
class Tester(models.Model):
	name = models.CharField(max_length=10)
	timestamp = models.DateTimeField(auto_now_add=True)
	

@receiver(pre_save, sender=Quiz)
def slugify_name(sender, instance, *args, **kwargs):
	instance.slug = slugify(instance.name)

# @receiver(post_save,sender=QuizTaker)
# def answering(sender,instance,created,*args,**kwargs):
# 	if created:
# 		pass
# 	else:
# 		if instance.date_finished is not None:
# 			print("herehere")
# 			instance.completed = True

@receiver(pre_save,sender=QuizTaker)
def answering(sender,instance,*args,**kwargs):

	if instance.date_finished is not None:
		instance.completed = True

# post_save.connect(answering, sender=QuizTaker)

