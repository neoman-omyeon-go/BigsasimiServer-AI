FROM python:3.8
ENV PYTHONUNBUFFERED 1

WORKDIR /app

## Install packages
COPY requirements.txt /app/
# RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# dependency
RUN apt-get update
RUN apt-get -y install libgl1-mesa-glx

## Copy all src files
COPY . /app/

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
