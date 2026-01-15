FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir pydantic-ai mcp streamlit python-dotenv nest-asyncio

# Copy app files and set ownership to a non-root user (created below)
COPY config.py deepwiki_client.py agent.py app.py ./

# Create a non-root user and group with a UID in the Choreo-allowed range and set ownership of /app
RUN groupadd -r appuser || true \
 && useradd -r -u 10001 -g appuser -d /app -s /sbin/nologin -c "App user" appuser || true \
 && chown -R appuser:appuser /app

EXPOSE 8501

ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true

# Run as non-root user (use numeric UID per Choreo/Checkov requirement)
USER 10001

CMD ["streamlit", "run", "app.py"]
