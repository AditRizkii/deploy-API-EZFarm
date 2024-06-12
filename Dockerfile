# start from python base image
FROM python:3.9-slim

# change working directory
WORKDIR /code

# add requirements file to image
COPY requirements.txt /code/
COPY .env /code/

# install python libraries
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# add python code
COPY ./app/ /code/app/

# specify default commands
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8080"]