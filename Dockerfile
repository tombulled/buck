FROM python:3.8

COPY buck buck
COPY poetry.lock poetry.lock 
COPY pyproject.toml pyproject.toml

RUN pip install poetry
RUN poetry install
RUN pip install .

RUN mkdir data && mkdir data/bucket

EXPOSE 8080

ENTRYPOINT ["python", "-m", "buck"]
CMD ["data", "--port", "8080", "--host", "0.0.0.0"]