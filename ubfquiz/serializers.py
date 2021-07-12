from ubfquiz.models import Quiz, QuizTaker, Question, Answer, UsersAnswer, QuizSlot
from student.models import Student
from student import serializers as studentserializers
from rest_framework import serializers
from django.db.models import Count
from datetime import datetime,timedelta
from pytz import timezone

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

class QuizSlotSerializer(serializers.ModelSerializer):

	class Meta:
		model = QuizSlot
		fields = '__all__'

class QuizMInSerializer(serializers.ModelSerializer):

	quizslot_set = QuizSlotSerializer(many=True)
	upcomingslot = serializers.SerializerMethodField()
	class Meta:
		model = Quiz
		fields =["id","slug","name","duration","quizslot_set","rollout_date"]

	def get_upcomingslot(self,obj):
		quizSlot =  QuizSlot.objects.filter(quiz=obj)
		now = timezone.now()
		#now = now + timedelta(hours=5,minutes=30)
		for slot in quizSlot:
			if now>=slot.start_datetime and now<=(slot.start_datetime+obj.duration):
				data={
					"starttime":(slot.start_datetime).strftime("%b %d %Y %H:%M:%S"),
					"endtime":(slot.start_datetime+obj.duration).strftime("%b %d %Y %H:%M:%S")
				}
				return data
			elif now<slot.start_datetime and now<(slot.start_datetime+obj.duration):
				data={
					"starttime":(slot.start_datetime).strftime("%b %d %Y %H:%M:%S"),
					"endtime":(slot.start_datetime+obj.duration).strftime("%b %d %Y %H:%M:%S")
				}
				return data

class QuizListSerializer(serializers.ModelSerializer):
	questions_count = serializers.SerializerMethodField()
	type = serializers.SerializerMethodField()
	islive = serializers.SerializerMethodField()
	currentslot = serializers.SerializerMethodField()
	nextslot = serializers.SerializerMethodField()
	quizslot_set = QuizSlotSerializer(many=True)
	rank = serializers.SerializerMethodField(read_only=True)
	completed = serializers.SerializerMethodField()
	day_rank= serializers.SerializerMethodField()
	class Meta:
		model = Quiz
		fields = ["id", "name", "description", "image", "slug", "questions_count", "price", "type","duration","live","islive","currentslot","nextslot","quizslot_set",'rank','completed','day_rank',"rollout_date"]
		read_only_fields = ["questions_count", "type","live"]

	def get_questions_count(self, obj):
		return obj.question_set.all().count()

	def get_type(self, obj):
		return "test"

	def get_islive(self,obj):
		quizSlot =  QuizSlot.objects.filter(quiz=obj)
		now = timezone.now()
		#now = now + timedelta(hours=5,minutes=30)
		for slot in quizSlot:
			# print(slot.id)
			# print(slot.start_datetime)
			# print("endtime")
			# print(slot.start_datetime+obj.duration)
			if now>=slot.start_datetime and now<=(slot.start_datetime+obj.duration):
				print("here")
				return True
		
		return False

	def get_currentslot(self,obj):
		data={}
		quizSlot =  QuizSlot.objects.filter(quiz=obj)
		now = timezone.now()
		#now = now + timedelta(hours=5,minutes=30)
		shift = timedelta(hours=5,minutes=30)
		for slot in quizSlot:
			if now>=slot.start_datetime and now<=(slot.start_datetime+obj.duration):

				data={
					"startTime":(slot.start_datetime+shift).strftime("%b %d %Y %H:%M:%S"),
					"duration":str(obj.duration),
					"endTime":(slot.start_datetime+obj.duration+shift).strftime("%b %d %Y %H:%M:%S")
				}
				return data
		
		return data

	def get_nextslot(self,obj):
		data={}
		quizSlot =  QuizSlot.objects.filter(quiz=obj)
		now = timezone.now()
		#now = now + timedelta(hours=5,minutes=30)
		shift = timedelta(hours=5,minutes=30)
		print(now)
		for slot in quizSlot:
			print(slot)
			if now<slot.start_datetime and now<(slot.start_datetime+obj.duration):
				print(obj.duration)
				data={
					"startTime":(slot.start_datetime+shift).strftime("%b %d %Y %H:%M:%S"),
					"duration":str(obj.duration),
					"endTime":(slot.start_datetime+obj.duration+shift).strftime("%b %d %Y %H:%M:%S")
				}
				return data
		
		return data
	
	def get_completed(self, obj):
		try:
			student = Student.objects.get(user=self.context['request'].user)
		except ObjectDoesNotExist:
			return None
		try:
			quiztaker = QuizTaker.objects.get(student=student, quiz=obj)
			return quiztaker.completed
		except QuizTaker.DoesNotExist:
			return None

	def get_rank(self, obj):
		try:
			student = Student.objects.get(user=self.context['request'].user)
		except ObjectDoesNotExist:
			return None
		try:
			quiztaker = QuizTaker.objects.get(student=student, quiz=obj)
		except:
			return None
		aggregate = QuizTaker.objects.filter(score__lt=quiztaker.score).aggregate(ranking=Count('score'))
		return aggregate['ranking'] + 1

	def get_day_rank(self,obj):
		try:
			student = Student.objects.get(user=self.context['request'].user)
		except ObjectDoesNotExist:
			return None
		try:
			quiztaker = QuizTaker.objects.get(student=student, quiz=obj)
		except:
			return None
		return quiztaker.quiz_day_rank

class QuizListSerializer2(serializers.ModelSerializer):
	questions_count = serializers.SerializerMethodField()
	type = serializers.SerializerMethodField()
	islive = serializers.SerializerMethodField()
	currentslot = serializers.SerializerMethodField()
	nextslot = serializers.SerializerMethodField()
	quizslot_set = QuizSlotSerializer(many=True)
	completed = serializers.SerializerMethodField()

	class Meta:
		model = Quiz
		fields = ["id", "name", "description", "image", "slug", "questions_count", "price", "type","duration","live","islive","currentslot","nextslot","quizslot_set","rollout_date","completed"]
		read_only_fields = ["questions_count", "type","live"]

	def get_questions_count(self, obj):
		return obj.question_set.all().count()

	def get_type(self, obj):
		return "test"

	def get_islive(self,obj):
		quizSlot =  QuizSlot.objects.filter(quiz=obj)
		#now = datetime.now()
		now = timezone.now()
		#now = now + timedelta(hours=5,minutes=30)
		for slot in quizSlot:
			# print(slot.id)
			# print(slot.start_datetime)
			# print("endtime")
			# print(slot.start_datetime+obj.duration)
			if now>=slot.start_datetime and now<=(slot.start_datetime+obj.duration):
				print("here")
				return True
		
		return False

	def get_currentslot(self,obj):
		data={}
		quizSlot =  QuizSlot.objects.filter(quiz=obj)
		#now = datetime.now()
		now = timezone.now()
		#now = now + timedelta(hours=5,minutes=30)
		shift = timedelta(hours=5,minutes=30)
		for slot in quizSlot:
			if now>=slot.start_datetime and now<=(slot.start_datetime+obj.duration):

				data={
					"startTime":(slot.start_datetime+shift).strftime("%b %d %Y %H:%M:%S"),
					"duration":str(obj.duration),
					"endTime":(slot.start_datetime+obj.duration+shift).strftime("%b %d %Y %H:%M:%S")
				}
				return data
		
		return data

	def get_nextslot(self,obj):
		data={}
		quizSlot =  QuizSlot.objects.filter(quiz=obj)
		#now = datetime.now()
		now = timezone.now()
		#now = now + timedelta(hours=5,minutes=30)
		shift = timedelta(hours=5,minutes=30)
		for slot in quizSlot:
			if now<slot.start_datetime and now<(slot.start_datetime+obj.duration):
				data={
					"startTime":(slot.start_datetime+shift).strftime("%b %d %Y %H:%M:%S"),
					"duration":str(obj.duration),
					"endTime":(slot.start_datetime+obj.duration+shift).strftime("%b %d %Y %H:%M:%S")
				}
				return data
		
		return data
	def get_completed(self, obj):
		try:
			student = Student.objects.get(user=self.context['request'].user)
		except ObjectDoesNotExist:
			return False
		try:
			quiztaker = QuizTaker.objects.get(student=student, quiz=obj)
			return quiztaker.completed
		except QuizTaker.DoesNotExist:
			return False
	

class AnswerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Answer
		fields = ["id", "question", "label"]


class QuestionSerializer(serializers.ModelSerializer):
	answer_set = AnswerSerializer(many=True)

	class Meta:
		model = Question
		fields = "__all__"


class UsersAnswerSerializer(serializers.ModelSerializer):
	class Meta:
		model = UsersAnswer
		fields = "__all__"


class MyQuizListSerializer(serializers.ModelSerializer):
	completed = serializers.SerializerMethodField()
	progress = serializers.SerializerMethodField()
	questions_count = serializers.SerializerMethodField()
	score = serializers.SerializerMethodField()
	type = serializers.SerializerMethodField()

	class Meta:
		model = Quiz
		fields = ["id", "name", "description", "image", "slug", "questions_count", "completed", "score", "progress", "price", "type"]
		read_only_fields = ["questions_count", "completed", "progress", "type"]

	def get_completed(self, obj):
		try:
			student = Student.objects.get(user=self.context['request'].user)
		except ObjectDoesNotExist:
			return None
		try:
			quiztaker = QuizTaker.objects.get(student=student, quiz=obj)
			return quiztaker.completed
		except QuizTaker.DoesNotExist:
			return None

	def get_progress(self, obj):
		try:
			student = Student.objects.get(user=self.context['request'].user)
		except ObjectDoesNotExist:
			return None
		try:
			quiztaker = QuizTaker.objects.get(student=student, quiz=obj)
			if quiztaker.completed == False:
				questions_answered = UsersAnswer.objects.filter(quiz_taker=quiztaker, answer__isnull=False).count()
				total_questions = obj.question_set.all().count()
				return int(questions_answered / total_questions)
			return None
		except QuizTaker.DoesNotExist:
			return None

	def get_questions_count(self, obj):
		return obj.question_set.all().count()

	def get_score(self, obj):
		try:
			student = Student.objects.get(user=self.context['request'].user)
		except ObjectDoesNotExist:
			return None
		try:
			quiztaker = QuizTaker.objects.get(student=student, quiz=obj)
			if quiztaker.completed == True:
				return quiztaker.score
			return None
		except QuizTaker.DoesNotExist:
			return None

	def get_type(self, obj):
		return "test"


class QuizTakerSerializer(serializers.ModelSerializer):
	usersanswer_set = UsersAnswerSerializer(many=True)
	rank = serializers.SerializerMethodField(read_only=True)
	correct_answers = serializers.SerializerMethodField(read_only=True)
	wrong_answers = serializers.SerializerMethodField(read_only=True)
	not_attempted = serializers.SerializerMethodField(read_only=True)
	time_spent = serializers.SerializerMethodField(read_only=True)
	student = studentserializers.StudentMinSerializer()
	class Meta:
		model = QuizTaker
		fields = "__all__"

	def get_rank(self, obj):
		aggregate = QuizTaker.objects.filter(quiz_id=obj.quiz,score__gt=obj.score).aggregate(ranking=Count('score'))
		return aggregate['ranking'] + 1 

	def get_correct_answers(self, obj):
		correct_answers = 0
		for users_answer in UsersAnswer.objects.filter(quiz_taker=obj):
			answer = Answer.objects.get(question=users_answer.question, is_correct=True)
			if users_answer.answer == answer:
				correct_answers += 1
		return correct_answers

	def get_wrong_answers(self, obj):
		wrong_answers = 0
		for users_answer in UsersAnswer.objects.filter(quiz_taker=obj, answer__isnull=False):
			answer = Answer.objects.get(question=users_answer.question, is_correct=True)
			if users_answer.answer != answer:
				wrong_answers += 1
		return wrong_answers

	def get_not_attempted(self, obj):
		not_attempted = UsersAnswer.objects.filter(quiz_taker=obj, answer__isnull=True).count()
		return not_attempted

	def get_time_spent(self, obj):
		if obj.completed:
			time = obj.date_finished - obj.timestamp
			return (time.seconds // 3600)
		else:
			return None

class QuizDetailSerializer(serializers.ModelSerializer):
	quizslot_set = QuizSlotSerializer(many=True)
	quiztakers_set = serializers.SerializerMethodField()
	question_set = QuestionSerializer(many=True)
	starttime = serializers.SerializerMethodField()
	endtime = serializers.SerializerMethodField()
	class Meta:
		model = Quiz
		fields = ["id","name","description", "image", "slug","price","duration","live","roll_out","rollout_date","quizslot_set","quiztakers_set","question_set","starttime","endtime"]

	def get_quiztakers_set(self, obj):
		try:
			student = Student.objects.get(user=self.context['request'].user)
		except ObjectDoesNotExist:
			return None
		try:
			quiztaker = QuizTaker.objects.get(student=student, quiz=obj)
			serializer = QuizTakerSerializer(quiztaker)
			return serializer.data
		except QuizTaker.DoesNotExist:
			return None
	
	def get_starttime(self,obj):
		change = timedelta(hours=5,minutes=30)
		try:
			student = Student.objects.get(user=self.context['request'].user)
		except ObjectDoesNotExist:
			return None
		try:
			quiztaker = QuizTaker.objects.get(student=student, quiz=obj)
		except QuizTaker.DoesNotExist:
			return None
		print(quiztaker.starttime)
		return (quiztaker.starttime+change).strftime("%b %d %Y %H:%M:%S")
	
	def get_endtime(self,obj):
		change = timedelta(hours=5,minutes=30)
		try:
			student = Student.objects.get(user=self.context['request'].user)
		except ObjectDoesNotExist:
			return None
		try:
			quiz_taker = QuizTaker.objects.get(student=student, quiz=obj)
		except QuizTaker.DoesNotExist:
			return None
		if obj.live:
			quizSlot =  QuizSlot.objects.filter(quiz=obj)
			for slot in quizSlot:
				if quiz_taker.starttime>=slot.start_datetime and quiz_taker.starttime<=(slot.start_datetime+obj.duration):
					return (slot.start_datetime+obj.duration+change).strftime("%b %d %Y %H:%M:%S")
				elif quiz_taker.starttime<slot.start_datetime and quiz_taker.starttime<(slot.start_datetime+obj.duration):
					return (slot.start_datetime+obj.duration+change).strftime("%b %d %Y %H:%M:%S")
		return (quiz_taker.starttime+obj.duration+change).strftime("%b %d %Y %H:%M:%S")

class QuizLeaderBoardSerializer(serializers.ModelSerializer):
	quiztakers_set = serializers.SerializerMethodField()

	class Meta:
		model = Quiz
		fields = ["id","name","description", "image", "slug","price","duration","live","roll_out","rollout_date","quiztakers_set"]

	def get_quiztakers_set(self, obj):
		try:
			quiz_taker = QuizTaker.objects.filter(quiz=obj)
			serializer = QuizTakerSerializer(quiz_taker, many=True)
			return serializer.data
		except QuizTaker.DoesNotExist:
			return None

class QuizResultSerializer(serializers.ModelSerializer):
	quiztaker_set = serializers.SerializerMethodField()
	question_set = QuestionSerializer(many=True)

	class Meta:
		model = Quiz
		fields = ["id","name","description", "image", "slug","price","duration","live","roll_out","rollout_date","quiztaker_set","question_set"]

	def get_quiztaker_set(self, obj):
		try:
			student = Student.objects.get(user=self.context['request'].user)
		except ObjectDoesNotExist:
			return None
		try:
			quiztaker = QuizTaker.objects.get(student=student, quiz=obj)
			serializer = QuizTakerSerializer(quiztaker)
			return serializer.data

		except QuizTaker.DoesNotExist:
			return None




