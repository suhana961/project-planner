from django.db import models

import uuid

from django_ckeditor_5.fields import CKEditor5Field

# Create your models here.

class BaseClass(models.Model):

    uuid = models.UUIDField(unique=True,default=uuid.uuid4)

    active_status = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        abstract = True

class Project(BaseClass):

    title = models.CharField(max_length=255)

    description = CKEditor5Field()

    documentation = models.FileField(upload_to='projects-documents')

    class Meta:

        verbose_name = 'Projects'

        verbose_name_plural = 'Projects'

    def __str__(self):

        return self.title

class AssignedProject(BaseClass):

    project = models.OneToOneField('Project',on_delete=models.PROTECT)

    coordinator = models.ForeignKey('authentication.Profile',on_delete=models.PROTECT,related_name='coordinator')

    developers = models.ManyToManyField('authentication.Profile',related_name='developers')

    duration = models.PositiveIntegerField()

    start_date = models.DateField()

    tentative_end_date = models.DateField()

    project_completed = models.BooleanField(default=False)

    class Meta:

        verbose_name = 'Assigned Projects'

        verbose_name_plural = 'Assigned Projects'

    def __str__(self):

        return f'{self.project.title}-{self.coordinator.first_name}'

class PriorityChoices(models.TextChoices):

    LOW = 'Low','Low'
    MEDIUM = 'Medium','Medium'
    HIGH = 'High','High'

class Task(BaseClass):

    title = models.CharField(max_length=225)

    description = models.TextField()

    assigned_project = models.ForeignKey('AssignedProject',on_delete=models.PROTECT,related_name='assigned_tasks')

    assigned_to = models.ForeignKey('authentication.Profile',on_delete=models.PROTECT)

    priority = models.CharField(max_length=10,choices=PriorityChoices.choices)

    duration = models.TimeField(null=True,blank=True)

    start_date = models.DateField(null=True,blank=True)

    end_date = models.DateField(null=True,blank=True)

    task_completed = models.BooleanField(default=False)

    class Meta:

        verbose_name = 'Tasks'

        verbose_name_plural  = 'Tasks'

    def __str__(self):
        return f'{self.title}-{self.assigned_to.first_name}'




