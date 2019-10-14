ARG PYTHON_IMAGE
ARG PYTHON_IMAGE_VERSION

FROM ${PYTHON_IMAGE}:${PYTHON_IMAGE_VERSION}

RUN pip install --upgrade pip setuptools

WORKDIR /opt/reprit

COPY reprit/ reprit/
COPY tests/ tests/
COPY README.md .
COPY requirements-tests.txt .
COPY setup.py .
COPY setup.cfg .

RUN pip install --force-reinstall -r requirements-tests.txt
