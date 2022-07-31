FROM python:3.8

COPY buck buck
COPY poetry.lock poetry.lock 
COPY pyproject.toml pyproject.toml

RUN pip install poetry
RUN poetry install
RUN pip install .

RUN mkdir data

EXPOSE 8080

CMD ["python", "-m", "buck", "data", "--port", "8080", "--host", "0.0.0.0"]