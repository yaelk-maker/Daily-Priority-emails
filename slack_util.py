#!/usr/bin/env python3
"""Slack utility using SLACK_BOT_TOKEN for both reading and sending messages.

Based on the send_via_bot_token pattern from Slack-BOT/slack_bot.py.

Usage:
  Send:  echo "message" | python3 slack_util.py send <channel_id>
  Read:  python3 slack_util.py read <channel_id> [--limit N]
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


SLACK_API = "https://slack.com/api"


def _api_call(method: str, token: str, params: dict | None = None, body: dict | None = None) -> tuple[bool, dict | str]:
    url = f"{SLACK_API}/{method}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    if body:
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    else:
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        return False, f"network error: {exc}"
    except json.JSONDecodeError:
        return False, "invalid response from Slack"
    if not result.get("ok"):
        return False, f"slack error: {result.get('error', 'unknown')}"
    return True, result


def send(token: str, channel: str, text: str) -> tuple[bool, str]:
    ok, result = _api_call("chat.postMessage", token, body={"channel": channel, "text": text})
    if not ok:
        return False, result
    return True, "ok"


def read(token: str, channel: str, limit: int = 5) -> tuple[bool, str]:
    ok, result = _api_call("conversations.history", token, params={"channel": channel, "limit": limit})
    if not ok:
        return False, result
    messages = result.get("messages", [])
    output_lines = []
    for msg in messages:
        text = msg.get("text", "")
        user = msg.get("user", "bot")
        ts = msg.get("ts", "")
        output_lines.append(f"[{ts}] {user}: {text}")
    return True, "\n".join(output_lines) if output_lines else "(no messages)"


def main() -> int:
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        print("slack_util.py: SLACK_BOT_TOKEN not set", file=sys.stderr)
        return 1

    if len(sys.argv) < 3:
        print("Usage:", file=sys.stderr)
        print("  echo 'msg' | python3 slack_util.py send <channel_id>", file=sys.stderr)
        print("  python3 slack_util.py read <channel_id> [--limit N]", file=sys.stderr)
        return 1

    command = sys.argv[1]
    channel = sys.argv[2]

    if command == "send":
        text = sys.stdin.read().strip() if not sys.stdin.isatty() else ""
        if not text:
            print("slack_util.py: no message on stdin", file=sys.stderr)
            return 1
        ok, detail = send(token, channel, text)
        if not ok:
            print(f"slack_util.py: {detail}", file=sys.stderr)
            return 1
        return 0

    elif command == "read":
        limit = 5
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit")
            if idx + 1 < len(sys.argv):
                limit = int(sys.argv[idx + 1])
        ok, detail = read(token, channel, limit)
        if not ok:
            print(f"slack_util.py: {detail}", file=sys.stderr)
            return 1
        print(detail)
        return 0

    else:
        print(f"slack_util.py: unknown command '{command}'", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
