

from django.db import models


# Create your models here.

from django.contrib.auth.models import AbstractUser

class RoleChoices(models.TextChoices):

  ADMIN = 'Admin','Admin'

  COORDINATOR = 'Project Coordinator','Project Coordinator'

  DEVELOPER = 'Developer','Developer'

class TechChoice(models.TextChoices):


  BACKEND = 'Backend','Backend'

  FRONTEND = 'Frontend Developer','Frontend Developer'

  FULLSTACK = 'Fullstack Developer','Fullstack Developer'

  UI_UX = 'UI/UX Devoloper','UI/UX Devoloper'

  TESTER = 'Software Tester','Software Tester'
  
class Profile(AbstractUser):

  role = models.CharField(max_length=20, choices=RoleChoices.choices)

  tech = models.CharField(max_length=50,choices=TechChoice.choices,null=True,blank=True)

  class Meta:

    verbose_name = 'Profiles'

    verbose_name_plural = 'Profiles'

  def __str__(self):
    
    return f'{self.first_name}-{self.tech}'