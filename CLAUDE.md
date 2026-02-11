# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Package manager:** `uv`

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run a single test file
uv run pytest tests/test_showroom_archiver.py

# Run a single test
uv run pytest tests/test_showroom_archiver.py::test_function_name

# Run all checks via invoke
uv run invoke test.all

# Linting
uv run invoke lint

# Style/formatting checks
uv run invoke style

# Deep analysis
uv run invoke lint.deep

# List all available invoke tasks
uv run invoke --list
```

**Running the application:**
```bash
showroom-podcast                  # Uses config.yml in current directory
showroom-podcast -f /path/to/config.yml
```

## Architecture

This is an async Python application that polls SHOWROOM live streaming rooms and archives them via FFmpeg.

### Data flow

```
CLI (click) -> ShowroomPodcast.run() -> asyncio.run(archive_repeatedly())
    -> ArchivingTaskManager.poll_all_rooms()
        -> ShowroomPoller.poll(room_id, lock)  [per room, 1s stagger]
            -> Polling.poll(room_id)            [API: is room live?]
            -> ShowroomArchiver.archive()       [if live and lock acquired]
                -> StreamingUrl.get_url_for_best_quality()  [API: get HLS URL]
                -> FFmpegCoroutine.execute()    [async subprocess via asynccpu]
```

### Key design decisions

**Concurrency model:** Each room gets a `threading.Lock` managed by a multiprocessing `Manager`. The lock is acquired non-blocking (`acquire(blocking=False)`) so that if archiving is already in progress for a room, the poll simply skips it. The FFmpeg subprocess itself runs via `asynccpu.ProcessTaskPoolExecutor` (CPU-bound task pool), controlled by `number_process` in config.

**Retry logic:** `ShowroomArchiver` retries up to 5 times using `ArchiveAttempter`, an async generator. Transient HTTP errors (502-504, DNS failures) raise `TemporaryNetworkIssuesError` and are retried; persistent failures raise `MaxRetriesExceededError`.

**Configuration:** `Config` (in `config.py`) extends `YamlDataClassConfig` — a dataclass whose fields are populated from `config.yml`. The global `CONFIG` instance in `showroompodcast/__init__.py` is mutated during `ShowroomPodcast.__init__()`.

**API layer:** Both `Polling` and `StreamingUrl` extend `ShowroomApi`, which sets up a `requests.Session` with `urllib3.Retry` for HTTP-level retries with exponential backoff.

**Output files:** Archives saved to `./output/{room_id}-{timestamp_jst}.mp4`

### Module map

| Module | Responsibility |
|--------|---------------|
| `cli.py` | Click entry point |
| `showroom_podcast.py` | Top-level orchestrator, Slack error reporting |
| `archiving_task_manager.py` | Per-room lock management, task spawning |
| `showroom_poller.py` | Poll one room, acquire lock, start archive |
| `showroom_archiver.py` | FFmpeg archiving with retry |
| `showroom_stream_spec_factory.py` | Build ffmpeg-python `StreamSpec` from room ID |
| `api/polling.py` | SHOWROOM API: check if room is on live |
| `api/streaming_url.py` | SHOWROOM API: get best-quality HLS stream URL |
| `slack/slack_client.py` | Post error notifications to Slack |
| `config.py` | YAML-based configuration dataclasses |
| `exceptions.py` | `TemporaryNetworkIssuesError`, `MaxRetriesExceededError` |

## Testing

Tests use `pytest` with `pytest-asyncio` and `pytest-mock`. Key fixtures in `tests/conftest.py`:

- `MockFFmpegCoroutine` — replaces the async FFmpeg subprocess
- `MockPolling` — mocks HTTP responses for the polling API (`requests-mock`)
- `MockStreamingUrl` — mocks HTTP responses for the stream URL API
- `MockSlackWebClient` — replaces Slack SDK calls

Slow tests can be marked with `@pytest.mark.slow`.

## Tooling

- **Ruff** — primary linter (select = ALL, line length 119). Per-file: tests ignore S101.
- **MyPy** — strict mode enabled; stubs ignored for `ffmpeg.*` and `urllib3.*`.
- **Flake8** — secondary linter with `flake8-bugbear`.
- **docformatter** — Google-style docstrings, wrap at 119 chars.
- Version uses timestamp format (`20241231044500`), managed by `bump-my-version`.
