# pull official base image
FROM python:3.8.5

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy app
COPY . .