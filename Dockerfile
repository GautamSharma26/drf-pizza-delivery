FROM python:3.8.13-bullseye

# set work directory
WORKDIR /usr/src/app

# set environment variables
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1

# install dependencies
#RUN ls -al
RUN pip install --upgrade pip
COPY ./requirements.txt .
#COPY ./requirements_dev.txt .
RUN pip install -r requirements.txt
COPY . .
#RUN . env/bin/activate

ENV DJANGO_SETTINGS_MODULE=pizza.settings
ENV PYTHONPATH=/code


RUN python3 manage.py migrate
RUN python3 manage.py collectstatic --no-input

# copy project
COPY . .

#CMD ["celery", "-A", "pizza", "worker", "--beat", "-l", "info"]
CMD =["python", "manage.py", "runserver"]
#Updated 22 Jan
