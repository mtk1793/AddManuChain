from django.db import models

# Use this import to implement Min, Max validators
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils.text import slugify
# Create your models here.

# In order to django let you use the database commands and connect with it, you have to use models.Model
# Product is the name of the table that we are going to work on
# In this table we declare the name of the columns that we need
# Here instead of giving names to the table itself, first we have to make some fundamentals in it and based on those, we can define and give values

# With doing any changes to the class that is related to the database we have to use makemigrations and migrate commnad
# to all of those changes be applied to the main dataset
class Product(models.Model):
    title = models.CharField(max_length=200)
    price = models.IntegerField()
    # Important thing about some of these sections are that they need
    # validation to be app;ied as they can't accept all numbers
    # For instance, rating only can accept numbers from 1 to 5
    # and we have to set validation to get them authority
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=0
    )
    short_description = models.CharField(max_length=350, null=True)
    is_active = models.BooleanField(default=True)

    # By using this command, we can have SlugField for our each product that instead of showing the id, it can use the slug id without manipulating the id itself
    # 3D Printer 1 --> 3D-Printer-1
    slug = models.SlugField(default="", null=False, db_index=True)


    def get_absolute_url(self):
        return reverse('product_detail',args=[self.slug])
    # STR def responsibility is to present the instance
    # We use this def to get log about the Product itself
    # If we use this command we have : <QuerySet [<Product: Product object (1)>, <Product: Product object (2)>]>
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.title} - {self.price}"