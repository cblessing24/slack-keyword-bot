FROM ubuntu:20.04

WORKDIR /slack-app

RUN apt-get update &&\
    apt-get install -y software-properties-common curl &&\
    add-apt-repository -y ppa:deadsnakes/ppa &&\
    apt-get install -y \
        python3.10 \
        python3.10-distutils \
        python3.10-venv &&\
    curl -O https://bootstrap.pypa.io/get-pip.py &&\
    python3.10 get-pip.py &&\
    rm get-pip.py &&\
    python3.10 -m pip install --upgrade pip &&\
    python3.10 -m pip install pdm &&\
    pdm config --local python.use_venv True &&\
    python3.10 -m venv .venv

COPY . .

RUN pdm install

CMD [".venv/bin/python3.10", "-m", "slack_app.entrypoints.slack_app.dev"]
