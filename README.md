# drf-pizza-delivery/Celery/Channels
#Channels #Celery #Signals these all are integrated in this project.This repository is part of backend of pizza delivery app. 

Channels:

Channels is used with the help of Redis
Channels is used in this project for updating status of ordered pizza items.
Signals also played important role with channels in this project.

Celery:

Celery is also used in this for performing background task.
For Celery I used Redis in this for storing Celery Task information.
Redis is also used here for message passing as a message broker in celery.

Commands for Celery:

To start worker : celery -A project_name worker

To start beat   : celery -A project_name beat

project_name : This is the root folder of project where you put your celery.py file.

Tip: Always use redis as a password protected on server either it will give warning or error sometimes.
