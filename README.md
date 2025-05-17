# RFP Scraper

A tool for scraping and analyzing Request for Proposal (RFP) documents.

## Setup

This project uses [uv](https://github.com/astral-sh/uv) for Python package management.

```bash
# Ensure you have up installed
which uv || pip intall uv

# Create a virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate  # On Unix/macOS

# Install dependencies
# NB: <-- if you ever appear to have missing dependencies this is the command you likely want
uv sync
```

## Usage

We install the `rfp` comamnd as a script -- its defined in the `rfp_scraper/cli/__main__.py` file. It uses [typer](https://typer.tiangolo.com/tutorial/)

Run `rfp --help` to see all commands and subcommands.

Example:

```bash
rfp scrape sam
```

## Development

# Run tests

```bash
pytest
```
