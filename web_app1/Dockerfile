FROM python:3.8-alpine
COPY ./nahual /app
WORKDIR /app
#RUN pip install
RUN pip install flask
RUN pip install sqlalchemy
RUN pip install wtforms
EXPOSE 8000
CMD python ./app.py