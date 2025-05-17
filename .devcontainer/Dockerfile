FROM python:3.12-slim

SHELL [ "/bin/bash", "-c" ]

ENV SHELL=/bin/bash
ENV PATH="/workspace/.venv/bin:$PATH"

# Install necessary packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    git-lfs \
    pgcli \
    postgresql-client \
    vim \
    && echo "Done"

# Set up a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Install uv
RUN pip install uv && uv venv

# Set the working directory
WORKDIR /workspace
