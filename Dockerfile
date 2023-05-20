FROM python:3.11.2

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

COPY ./setup.py /code/setup.py

COPY ./src /code/src

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD [ "uvicorn", "src.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
