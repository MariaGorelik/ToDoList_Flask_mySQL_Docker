FROM python:latest
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY templates /app/templates
COPY app.py .
ENTRYPOINT ["python"]
CMD ["app.py"]