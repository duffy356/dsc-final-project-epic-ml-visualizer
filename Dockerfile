FROM python:3.8-slim

MAINTAINER "duffy356"

RUN apt-get update && apt-get install -y curl

COPY download_models.sh .
RUN chmod +x /download_models.sh

RUN /download_models.sh

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE ${STREAMLIT_SERVER_PORT}
RUN --mount=type=secret,id=PICKLE_PW \
   cat /run/secrets/PICKLE_PW

run export PICKLE_PW=$(cat /run/secrets/PICKLE_PW)

CMD ["streamlit", "run", "main.py"]
