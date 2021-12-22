# Build local
# docker image build . -t tigertag
# Verify local contents
# docker run -it --rm tigertag bash
# Send to Dockerhub
# docker image build . -t hedrickbt/tigertag:latest -t hedrickbt/tigertag:$(< version.txt)
# docker push hedrickbt/tigertag:latest
# docker push hedrickbt/tigertag:$(< version.txt)
# Run
# check docker-compose.yml
FROM python:3.10-slim-bullseye

RUN apt-get update

WORKDIR /app
ADD alembic.ini main.py LICENSE README.txt requirements.txt /app/
ADD alembic /app/alembic
ADD tigertag /app/tigertag
ADD entrypoint.sh /scripts/entrypoint.sh
RUN pip install -r requirements.txt

CMD ["/scripts/entrypoint.sh"]