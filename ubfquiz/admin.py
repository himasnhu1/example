from django.contrib import admin
import nested_admin
from .models import Quiz, Question, Answer, QuizTaker, UsersAnswer, QuizSlot,Tester


class AnswerInline(nested_admin.NestedTabularInline):
	model = Answer
	extra = 4
	max_num = 4


class QuestionInline(nested_admin.NestedTabularInline):
	model = Question
	inlines = [AnswerInline,]
	extra = 5

class QuizSlotInLine(nested_admin.NestedTabularInline):
	model = QuizSlot
	extra =0

class QuizAdmin(nested_admin.NestedModelAdmin):
	inlines = [QuizSlotInLine,QuestionInline,]


class UsersAnswerInline(admin.TabularInline):
	model = UsersAnswer


class QuizTakerAdmin(admin.ModelAdmin):
	inlines = [UsersAnswerInline,]


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QuizTaker, QuizTakerAdmin)
admin.site.register(UsersAnswer)
admin.site.register(QuizSlot)
admin.site.register(Tester)

