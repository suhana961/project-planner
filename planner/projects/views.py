from django.shortcuts import render
from uuid import UUID
from django.db.models import Q

from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.exceptions import ValidationError

from .models import Project 

from .serializers import ProjectSerializer

from .models import AssignedProject

from .serializers import AssignedProjectSerializer

from .serializers import TaskSerializer

from .models import Task

from rest_framework.views import APIView

from rest_framework.response import Response

from planner.utils import generate_tasks

from django.db import transaction

from planner.paginations import CustomPagination
# from authentication.models import Profile

# Create your views here.

class ProjectListCreateView(ListCreateAPIView):

    pagination_class = CustomPagination

    queryset = Project.objects.filter(active_status = True)

    serializer_class = ProjectSerializer

class ProjectRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):

    lookup_field = 'uuid'

    queryset = Project.objects.filter(active_status = True)

    serializer_class = ProjectSerializer

    def perform_destroy(self, instance):

        instance.active_status = False

        instance.save()

class AssignProjectListCreateView(ListCreateAPIView):

    pagination_class = CustomPagination

    queryset = AssignedProject.objects.filter(active_status = True).select_related('project','coordinator').prefetch_related('developers')

    serializer_class = AssignedProjectSerializer

class AssignedProjectRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):

    lookup_field = 'uuid'

    queryset = AssignedProject.objects.filter(active_status = True).select_related('project','coordinator').prefetch_related('developers')

    serializer_class = AssignedProjectSerializer

    def perform_destroy(self, instance):

        instance.active_status = False

        instance.save()

class TaskListCreateView(ListCreateAPIView):

    pagination_class = CustomPagination

    def get_queryset(self):

        queryset = Task.objects.filter(active_status=True).select_related('assigned_project', 'assigned_to')
        project_uuid = self.request.query_params.get('project')

        if project_uuid is None:
            return queryset

        if project_uuid.endswith('/'):
            project_uuid = project_uuid[:-1]

        try:
            project_uuid = UUID(project_uuid)
        except ValueError as exc:
            raise ValidationError({'project': 'Enter a valid project UUID.'}) from exc

        return queryset.filter(
            Q(assigned_project__uuid=project_uuid)
            | Q(assigned_project__project__uuid=project_uuid)
        )

    serializer_class = TaskSerializer


class TaskRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):

    lookup_field = 'uuid'

    queryset = Task.objects.all().select_related('assigned_project','assigned_to')

    serializer_class = TaskSerializer

    def perform_destroy(self, instance):

        instance.active_status = False

        instance.save()

class TaskCreateWithAI(APIView):


    def post(self,request,*args,**kwargs):

        uuid = kwargs.get('uuid')

        try:
        

            assigned_project = AssignedProject.objects.get(uuid=uuid)

            result = generate_tasks(assigned_project)

            tasks = [Task(title=task.title,
                      description=task.description,
                      assigned_project=assigned_project,
                      assigned_to_id=task.developer_id,
                      priority=task.priority) for task in result.tasks]

            with transaction.atomic():

                Task.objects.bulk_create(tasks)

                data = {'msg':'Tasks assigned succesfully'}

                return Response(data,status=200)

        except Exception as e:

            print(e)

            data ={'msg':'Failed to create Tasks'}

            return Response(data,status=400)



