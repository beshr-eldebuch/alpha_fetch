# Dockerfile
FROM python:3.10
WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./app /code/app

COPY entrypoint.sh /code/

RUN chmod +x /code/entrypoint.sh

CMD ["/code/entrypoint.sh"]
