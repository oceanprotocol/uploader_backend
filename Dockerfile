FROM python:3.9

# set work directory
WORKDIR /usr/src/app

# install dependencies
RUN pip install --upgrade pip 
COPY ./requirements.txt /usr/src/app
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app
WORKDIR /usr/src/app/server

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
