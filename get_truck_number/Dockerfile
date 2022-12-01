FROM python:3.9

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel

COPY requirements.txt .
COPY main.py .
RUN pip install -r requirements.txt

CMD ["python","main.py"]