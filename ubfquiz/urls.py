from django.urls import path, re_path
from ubfquiz.api import *

app_name = 'ubfquiz'

urlpatterns = [

	path("quizzes/", QuizListAPI.as_view()),
	path("save-answer/", SaveUsersAnswer.as_view()),
	re_path(r"quizzes/(?P<slug>[\w\-]+)/$", QuizDetailAPI.as_view()),
	re_path(r"quizzes/(?P<slug>[\w\-]+)/leaderboard/$", QuizLeaderBoardAPI.as_view()),
	re_path(r"quizzes/(?P<slug>[\w\-]+)/submit/$", SubmitQuizAPI.as_view()),

	path("dummy-quiz/",dummyquizchecker.as_view()),
]