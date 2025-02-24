#
# MIT License
#
# (C) Copyright 2019-2022, 2024-2025 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
FROM artifactory.algol60.net/docker.io/alpine:3.21 AS service
WORKDIR /app
ENV VIRTUAL_ENV=/app/venv
COPY constraints.txt requirements.txt dist/*.whl /app/
RUN apk add --upgrade --no-cache apk-tools && \
    apk update && \
    apk add --no-cache linux-headers gcc g++ python3 python3-dev py3-pip musl-dev libffi-dev openssl-dev git jq curl openssh-client && \
    apk -U upgrade --no-cache && \
    python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN --mount=type=secret,id=netrc,target=/root/.netrc \
    python3 -m pip install --no-cache-dir --upgrade pip -c constraints.txt && \
    python3 -m pip list --format freeze && \
    python3 -m pip install --no-cache-dir --disable-pip-version-check --upgrade wheel -c constraints.txt && \
    python3 -m pip list --format freeze && \
    python3 -m pip install --no-cache-dir --disable-pip-version-check -r requirements.txt && \
    python3 -m pip list --format freeze && \
    python3 -m pip install --no-cache-dir --disable-pip-version-check -c constraints.txt /app/*.whl && \
    python3 -m pip list --format freeze && \
    rm /app/*.whl /app/constraints.txt /app/requirements.txt
USER nobody:nobody
ENTRYPOINT [ "python3", "-m", "cfsssh.setup.service" ]
