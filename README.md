# Daily Priority Emails — ERP Summary Routine

Automated Claude Routine that runs daily at **8:35 AM GMT+3** to summarize Priority ERP system emails and post a digest to Slack.

## What it does

1. Searches Gmail for today's automated emails from `priority@maelyscosmetics.com`
2. Reads extracted reports from Google Drive ("Priority Daily Reports" folder)
3. Fetches yesterday's Consignment Gaps count from Slack
4. Posts a single summary message to Slack channel `#priority-daily-alerts-summary`

## Connectors required

- Gmail
- Google Drive
- Slack

## Expected daily emails (6)

| # | Subject (Hebrew) | Type | Data source |
|---|-----------------|------|-------------|
| 1 | לוג הזמנות לקוח CRM | CRM Orders Log | Email body (inline) |
| 2 | לוג קבלות CRM | CRM Receipts Log | Email body (inline) |
| 3 | שגיאות בטעינה חשבוניות CRM | CRM Invoice Loading Errors | HTM attachment → Google Drive doc |
| 4 | שגיאות בטעינה קבלות CRM | CRM Receipt Loading Errors | HTM attachment → Google Drive doc |
| 5 | דוח פערי קונסיגנציה | Daily Consignment Gaps Report | HTM attachment → Google Drive doc |
| 6 | סיכום ת.משלוח למחסן ליום קודם | Warehouse Shipment Summary | HTM attachment → Google Drive doc |

## Warehouse codes

| Code | Location |
|------|----------|
| 333 | NJ |
| 444 | Boston |
| 666 | Arizona |
| 888 | UK |
| 999 | KLB |

## Known issues

- **Deferred tool schema loading causes stalls in scheduled runs** — the routine requires `ToolSearch` calls to load MCP tool schemas, which block waiting for human input. Reported to Anthropic (GitHub issue, April 2026). Workaround: pre-authorize read-only MCP tools in `.claude/settings.json`.
