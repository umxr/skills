FROM python:3.11-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src ./src
ENV PYTHONPATH=/srv/src
CMD ["uvicorn", "ledgerline.main:app", "--host", "0.0.0.0", "--port", "8080"]
