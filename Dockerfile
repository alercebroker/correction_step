FROM python:3.6

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

RUN git clone https://github.com/vishnubob/wait-for-it.git helper

WORKDIR /app
COPY . /app

WORKDIR /app/scripts

CMD ["python", "run_step.py"]
