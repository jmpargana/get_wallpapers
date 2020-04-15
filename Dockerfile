FROM python:3.8

RUN mkdir /app
WORKDIR "/app"

RUN pip install pipenv
USER 1000

ADD Pipfile* reqwall.py /app/.

RUN pipenv install

CMD ["pipenv run python", "reqwall.py"]
