# For using the sqlite first we have to define classes of the columns that we want to use
# then we have to add the module itself in setting.py

# All of the changes that you have been done through your models should be
# informed to the dataset. This matter will be done using migrations inside
# each module


# The files that we have inside the migration folder of the specific models
# are the ones that automatically were made due to sensing any changes in the models.py
# of that model.

# In order to have this file inside our model we have to go into the terminal
# and use the commnad of "python manage.py makemigrations" to let django sense
# any changes and apply it over the migration files

# After finishing all of those changes and by checking them, we can use this command
# "python manage.py migrate" to apply all of those into the sqlite file and making a database file for us

# CRUD

# Till 36
