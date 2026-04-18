#!/usr/bin/env python3
"""Send a Slack message using SLACK_BOT_TOKEN (chat.postMessage API).

Based on the send_via_bot_token pattern from Slack-BOT/slack_bot.py.
Usage: echo "message" | python3 send_slack.py <channel_id>
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

SLACK_POST_URL = "https://slack.com/api/chat.postMessage"


def send(token: str, channel: str, text: str) -> tuple[bool, str]:
    data = json.dumps({"channel": channel, "text": text}).encode("utf-8")
    req = urllib.request.Request(
        SLACK_POST_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        return False, f"network error: {exc}"
    except json.JSONDecodeError:
        return False, "invalid response from Slack"
    if not body.get("ok"):
        return False, f"slack error: {body.get('error', 'unknown')}"
    return True, "ok"


def main() -> int:
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        print("send_slack.py: SLACK_BOT_TOKEN not set", file=sys.stderr)
        return 1

    channel = sys.argv[1] if len(sys.argv) > 1 else ""
    if not channel:
        print("Usage: echo 'message' | python3 send_slack.py <channel_id>", file=sys.stderr)
        return 1

    text = sys.stdin.read().strip() if not sys.stdin.isatty() else ""
    if not text:
        print("send_slack.py: no message on stdin", file=sys.stderr)
        return 1

    ok, detail = send(token, channel, text)
    if not ok:
        print(f"send_slack.py: {detail}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
