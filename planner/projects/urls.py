from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.ProjectListCreateView.as_view()),
    path('projects/<uuid:uuid>/', views.ProjectRetrieveUpdateDestroyView.as_view()),

    path('assigned_project/', views.AssignProjectListCreateView.as_view()),
    path('assigned_project/<uuid:uuid>/', views.AssignedProjectRetrieveUpdateDestroyView.as_view()),

    path('tasks/', views.TaskListCreateView.as_view()),
    path('tasks/<uuid:uuid>/', views.TaskRetrieveUpdateDestroyView.as_view()),
    path('create-tasks-ai/<uuid:uuid>/', views.TaskCreateWithAI.as_view()),
]