from django.db import models
from datetime import datetime
import string
import random

categories = [
    ('I', 'Income'),
    ('E', 'Expense'),
]

def generate_seed(length=20):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

# Create your models here.
class Transactions(models.Model):
    description = models.CharField(max_length=1000, default = '')
    category = models.CharField(max_length=100,choices=categories, default = 'I')
    amount = models.IntegerField(default=0)
    date = models.DateField(default=datetime.today)
    created = models.DateTimeField(default=datetime.today)
    updated = models.DateTimeField(auto_now=True)
    userSeed = models.CharField(max_length=1000, default = '')
    
    def __str__(self):
     return ' - '.join([str(i) for i in [self.id,self.description,self.userSeed] if i is not None])
    

class Users(models.Model):
    name = models.CharField(max_length=20,default='')
    lastName = models.CharField(max_length=20,default='')
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    seed = models.CharField(max_length=20, default=generate_seed, unique=True)

    def __str__(self):
        return self.username