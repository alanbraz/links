FROM registry.access.redhat.com/ubi9/python-311

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .
COPY links.yaml .

EXPOSE 8080

CMD CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]