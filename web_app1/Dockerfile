FROM python:3.8-alpine
COPY ./nahual_inscripcion /app
WORKDIR /app
#RUN pip install
RUN pip install flask
RUN pip install sqlalchemy
EXPOSE 8000
CMD python ./app.py