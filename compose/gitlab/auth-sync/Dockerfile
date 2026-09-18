FROM python:3.14-alpine

WORKDIR /app
COPY sync.py /app/sync.py

# Compose bind-mounts local secret files with the host owner. The Compose
# service therefore uses the unprivileged host UID 1000; it is otherwise
# read-only, has no capabilities, no socket and no exposed ports.
ENTRYPOINT ["python", "/app/sync.py"]
