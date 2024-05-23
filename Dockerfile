FROM python:3.8
ENV PYTHONUNBUFFERED 1

WORKDIR /app

## Install packages
COPY requirements_longtimetooooo.txt /app/
COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip cache purge

# need long time lib - commit container...
# RUN pip install --no-cache-dir -r requirements_longtimetooooo.txt
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu


RUN pip install --no-cache-dir -r requirements.txt

# dependency
RUN apt-get update
RUN apt-get -y install libgl1-mesa-glx

RUN pip install torchvision==0.14.1
RUN pip install lmdb nltk natsort

## Copy all src files
COPY . /app/

EXPOSE 8001

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
CMD ["python", "main.py"]
