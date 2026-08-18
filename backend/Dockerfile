FROM python:3.12-slim-bookworm

ARG PANDOC_VERSION=3.9.0.2
ARG PANDOC_SHA256=ce4ac48f48aa7eadc1f5dbdf3449a1739f188ecb8c5421c5adc070fe7479e567

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates curl \
    && curl --fail --location --output /tmp/pandoc.deb \
       "https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-1-amd64.deb" \
    && echo "${PANDOC_SHA256}  /tmp/pandoc.deb" | sha256sum --check --strict \
    && dpkg --install /tmp/pandoc.deb \
    && rm --force /tmp/pandoc.deb \
    && apt-get purge --yes --auto-remove curl \
    && rm --recursive --force /var/lib/apt/lists/*

WORKDIR /app/backend

COPY backend/requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip==26.2.1 \
    && python -m pip install --no-cache-dir --requirement requirements.txt

COPY backend/app ./app
COPY templates /app/templates

RUN groupadd --gid 10001 ai2doc \
    && useradd --create-home --uid 10001 --gid 10001 ai2doc \
    && mkdir --parents /tmp/ai2doc \
    && chown --recursive ai2doc:ai2doc /tmp/ai2doc

USER ai2doc
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
