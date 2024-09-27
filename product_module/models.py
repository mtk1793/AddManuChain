from django.db import models

# Create your models here.

# In order to django let you use the database commands and connect with it, you have to use models.Model
# Product is the name of the table that we are going to work on
# In this table we declare the name of the columns that we need
# Here instead of giving names to the table itself, first we have to make some fundamentals in it and based on those, we can define and give values
class Product(models.Model):
    title = models.CharField(max_length=200)
    price = models.IntegerField()