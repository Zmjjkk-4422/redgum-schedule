FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

# Configuration is supplied through environment variables at run time;
# no secrets are baked into the image.
ENV FLASK_CONFIG=production
ENV DATABASE=/data/redgum.db
VOLUME ["/data"]

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
