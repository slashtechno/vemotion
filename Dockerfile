FROM python:3.12-slim-bookworm
RUN apt update && apt install libgl1  libglib2.0-0 -y
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app
WORKDIR /app
RUN uv sync --frozen
ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "vemotion"]
EXPOSE 8000