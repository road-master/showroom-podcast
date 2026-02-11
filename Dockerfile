FROM futureys/claude-code-python-development:20260201121000
RUN apt-get update && apt-get install -y ffmpeg
COPY pyproject.toml /workspace/
# - Installation fails on Python 3.14 · Issue #327 · PyCQA/docformatter
#   https://github.com/PyCQA/docformatter/issues/327
RUN uv sync --python 3.13
