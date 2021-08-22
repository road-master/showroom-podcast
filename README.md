# SHOWROOM Podcast

[![Test](https://github.com/road-master/showroom-podcast/workflows/Test/badge.svg)](https://github.com/road-master/showroom-podcast/actions?query=workflow%3ATest)
[![Test Coverage](https://api.codeclimate.com/v1/badges/3aa628f353f2b70a3ff3/test_coverage)](https://codeclimate.com/github/road-master/showroom-podcast/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/3aa628f353f2b70a3ff3/maintainability)](https://codeclimate.com/github/road-master/showroom-podcast/maintainability)
[![Code Climate technical debt](https://img.shields.io/codeclimate/tech-debt/road-master/showroom-podcast)](https://codeclimate.com/github/road-master/showroom-podcast)
[![Updates](https://pyup.io/repos/github/road-master/showroom-podcast/shield.svg)](https://pyup.io/repos/github/road-master/showroom-podcast/)
[![Python versions](https://img.shields.io/pypi/pyversions/showroompodcast.svg)](https://pypi.org/project/showroompodcast)
[![Twitter URL](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2Froad-master%2Fshowroom-podcast)](http://twitter.com/share?text=SHOWROOM%20Podcast&url=https://pypi.org/project/showroompodcast/&hashtags=python)

Automatic archiver for SHOWROOM live which is listed by YAML file.

## Advantage

- Waits for on live, automatic archiving
- Archives multiple lives at same time

## Waits for on live, automatic archiving

Process waits for rooms on live. When live are started, process will automatically start archiving. Even if live was suddenly start during you are busy, you will be free from non-essential and non-urgent call, you can concentrate your task.

## Archives multiple lives at same time

It's possible to archive multiple lives at same time as much as CPU resource is supplied. You can check each content in order without watch at same time.

## Requirement

- [FFmpeg]

## Quickstart

### 1. Install

```console
pip install showroompodcast
```

### 2. Create `config.yml`

```yaml
# How much numbers of live record at same time.
number_process: ?

# List up tracking room ID to track for archive.
list_room_id:
  - ??????
  - ??????
  - ??????
  - ??????
  - ??????

# When set, process will report to Slack when process down for any reason.
slack:
  bot_token: xoxb-123456789012-345678901234-567890abcdefghijklmnopqr
  channel: ABCDEFGHI
```

### 3. Create `output` directory

```console
mkdir output
```

So far, the directory structure looks like this:

```text
your-workspace/
+----output/
+----config.yml
```

### 4. Execute command to run

```console
showroom-podcast
```

Then, process will automatically archive live into `output` directory when live has started.

Note that the process consumes packets even while waiting to track room whether on live or not.
Be ensure network especially when using it on a mobile line.

### 5. When shutdown process, send `Ctrl + C` in terminal

[FFmpeg]: https://ffmpeg.org/download.html
