from django.db import models


# Create your models here.
class Commands(models.Model):
    RUNS = (
        ('O', 'Once'),
        ('M', 'Multiple')
    )
    command = models.CharField(max_length=50, unique=True)
    runs = models.CharField(max_length=1, choices=RUNS)
    run_times = models.PositiveSmallIntegerField(default=0)
    last_run = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.command
