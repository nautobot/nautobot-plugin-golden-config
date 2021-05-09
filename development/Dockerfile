ARG python_ver=3.7
FROM python:${python_ver}

# Set env vars that won't change per image
ENV PYTHONUNBUFFERED=1 \
    PATH="/root/.poetry/bin:$PATH" \
    NAUTOBOT_CONFIG="/source/development/nautobot_config.py"

RUN pip install --upgrade pip\
  && pip install poetry

# -------------------------------------------------------------------------------------
# Install Nautobot Plugin
# -------------------------------------------------------------------------------------
RUN mkdir -p /source
WORKDIR /source
COPY . /source
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi
