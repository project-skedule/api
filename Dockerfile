FROM base:latest

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir /skedule-api
WORKDIR /skedule-api
COPY . /skedule-api/
CMD gunicorn --worker-class uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:8009 main:app