FROM python:3.9-slim-buster
RUN apt update --no-install-recommends -y
RUN apt install --no-install-recommends -y software-properties-common
RUN apt install --no-install-recommends -y curl build-essential
RUN apt install --no-install-recommends -y wget iputils-ping

RUN wget https://downloads.mariadb.com/MariaDB/mariadb_repo_setup
RUN echo "fd3f41eefff54ce144c932100f9e0f9b1d181e0edd86a6f6b8f2a0212100c32c mariadb_repo_setup" | sha256sum -c -
RUN chmod +x mariadb_repo_setup
RUN ./mariadb_repo_setup --mariadb-server-version="mariadb-10.5"
RUN apt update
RUN apt install -y libmariadb3 libmariadb-dev 

ENV TZ="Europe/Moscow" \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir /skedule-api
WORKDIR /skedule-api
COPY . /skedule-api/
CMD gunicorn --worker-class uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:8009 main:app