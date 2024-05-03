# Dockerfile
FROM python:3.10
WORKDIR /code

COPY ./requirements.txt ./entrypoint.sh /code/

RUN chmod +x /code/entrypoint.sh && \
    pip install --no-cache-dir -r /code/requirements.txt

COPY ./app /code/app

CMD ["/bin/sh", "/code/entrypoint.sh"]

