from django.db import models

# Create your models here.
class Admin(models.Model):
    email = models.EmailField()
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.email)