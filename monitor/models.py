from django.db import models

# Create your models here.


class Instance(models.Model):
    name = models.TextField()
    mac = models.TextField()
    local_ip = models.TextField()
    
    def __str__(self):
        return self.name + ' - ' + self.mac + ' - ' + self.local_ip

class Entry(models.Model):
    rate = models.IntegerField()
    instance = models.ForeignKey("Instance", on_delete=models.SET_NULL, null=True)
