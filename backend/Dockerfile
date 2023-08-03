FROM python:3.10

WORKDIR /app

COPY requirements/requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

RUN chmod +x entrypoint.sh

CMD [ "/bin/bash", "entrypoint.sh" ]