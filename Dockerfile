# start from python base image
FROM python:3.9-slim

# change working directory
WORKDIR /code

# add requirements file to image
COPY requirements.txt /code/
COPY .env /code/
COPY capstone-ezfarm-251b993be76d.json /code/capstone-ezfarm-251b993be76d.json

# Set the environment variable
ENV GOOGLE_APPLICATION_CREDENTIALS="/code/capstone-ezfarm-251b993be76d.json"

# install python libraries
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# add python code
COPY ./app/ /code/app/

# specify default commands
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8080"]