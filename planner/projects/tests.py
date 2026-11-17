from datetime import date
from unittest.mock import Mock, patch
from uuid import UUID

from django.db.models import Q
from django.test import SimpleTestCase, TestCase
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.test import APIClient, APIRequestFactory

from authentication.models import Profile
from .models import AssignedProject, Project, Task
from .views import TaskListCreateView


class TaskListCreateViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = TaskListCreateView()

    @patch('projects.views.Task.objects')
    def test_lists_active_tasks_when_project_is_not_provided(self, task_manager):
        queryset = Mock()
        task_manager.filter.return_value.select_related.return_value = queryset
        self.view.request = Request(self.factory.get('/tasks/'))

        result = self.view.get_queryset()

        self.assertIs(result, queryset)
        task_manager.filter.assert_called_once_with(active_status=True)

    @patch('projects.views.Task.objects')
    def test_filters_by_project_uuid_with_trailing_slash(self, task_manager):
        queryset = Mock()
        filtered_queryset = Mock()
        task_manager.filter.return_value.select_related.return_value = queryset
        queryset.filter.return_value = filtered_queryset
        project_uuid = UUID('5c4ba7af-06ea-4f8c-a213-c9f16e7de103')
        self.view.request = Request(
            self.factory.get('/tasks/', {'project': f'{project_uuid}/'})
        )

        result = self.view.get_queryset()

        self.assertIs(result, filtered_queryset)
        queryset.filter.assert_called_once()
        self.assertEqual(
            queryset.filter.call_args.args[0],
            Q(assigned_project__uuid=project_uuid)
            | Q(assigned_project__project__uuid=project_uuid),
        )

    @patch('projects.views.Task.objects')
    def test_rejects_invalid_project_uuid(self, task_manager):
        self.view.request = Request(
            self.factory.get('/tasks/', {'project': 'not-a-uuid'})
        )

        with self.assertRaises(ValidationError):
            self.view.get_queryset()

        task_manager.filter.return_value.select_related.return_value.filter.assert_not_called()


class TaskListResponseTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        coordinator = Profile.objects.create_user(
            username='coordinator',
            password='password',
            role='Project Coordinator',
            first_name='Coordinator',
        )
        developer = Profile.objects.create_user(
            username='developer',
            password='password',
            role='Developer',
            first_name='Developer',
        )
        project = Project.objects.create(
            title='Example project',
            description='Project description',
            documentation='example.pdf',
        )
        self.assigned_project = AssignedProject.objects.create(
            project=project,
            coordinator=coordinator,
            duration=10,
            start_date=date(2026, 1, 1),
            tentative_end_date=date(2026, 1, 11),
        )
        self.assigned_project.developers.add(developer)
        Task.objects.create(
            title='Example task',
            description='Task details',
            assigned_project=self.assigned_project,
            assigned_to=developer,
            priority='High',
        )

    def test_list_response_includes_task_and_related_details(self):
        response = self.client.get('/tasks/')

        self.assertEqual(response.status_code, 200)
        task = response.data[0]
        self.assertEqual(task['title'], 'Example task')
        self.assertEqual(task['description'], 'Task details')
        self.assertEqual(task['assigned_project']['project']['title'], 'Example project')
        self.assertEqual(task['assigned_to']['username'], 'developer')

    def test_project_uuid_filters_tasks(self):
        project_uuids = (
            self.assigned_project.project.uuid,
            self.assigned_project.uuid,
        )
        for project_uuid in project_uuids:
            response = self.client.get('/tasks/', {'project': str(project_uuid)})

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]['title'], 'Example task')
