FROM python:3.12-alpine3.19

RUN apk update && apk add texmf-dist texlive-full

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install -r requirements.txt

COPY . /code/

# Set the working directory

ENTRYPOINT ["python3", "main.py" ]
