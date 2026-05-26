# Playbook — Hatch AI Conversation Audit

Automated system that monitors every completed Hatch AI conversation, scores it against PPP's chatbot instructions, and surfaces issues to a review dashboard. Replaces manual weekly sampling with 100% coverage and same-day analysis.

---

## Architecture

```
Hatch (webhook: Assistant Conversation Completed)
    → Google Apps Script (receiver + async queue via 1-min trigger)
    → Claude API (analyzes conversation against chatbot instructions)
    → Google Sheet "Live Issues" tab (color-coded by severity)
```

No external hosting required — Apps Script runs entirely within Google Sheets.

---

## Why Apps Script (not a standalone server)

- Hatch webhooks fire on conversation end; Apps Script receives them as a web app endpoint
- A 1-minute trigger drains a queue sheet, batching Claude API calls asynchronously (avoids Hatch webhook timeout)
- Keeps everything in Google Workspace — no Render, no AWS, no maintenance overhead

---

## Setup Steps

1. Create a Google Sheet with a "Live Issues" tab and a queue tab
2. Open **Extensions → Apps Script**, paste the audit script
3. Add Script Property `ANTHROPIC_API_KEY` (gear icon → Script Properties)
4. Run `setup()` — creates the 1-min trigger and initializes sheet tabs
5. Run `testWithSamplePayload()` — verify a row appears in Live Issues
6. **Deploy → New Deployment → Web App**
   - Execute as: Me
   - Who has access: Anyone
   - Copy the Web App URL
7. In Hatch: **App Marketplace → Webhooks → Add Webhook**
   - Event: `Assistant Conversation Completed`
   - URL: the Web App URL from step 6

---

## Hatch Webhook Payload — Key Fields

> These fields were verified via DevTools inspection of Hatch's webhook preview in their UI. Confirm against a live payload before building, as Hatch doesn't document them publicly.

| Field | Value |
|-------|-------|
| `messages[]` | Full conversation array |
| `status` | Conversation status |
| `contact.name` | Customer name |
| `campaign.name` | Active campaign |
| `occurred_at` | Timestamp |
| `role: "assistant"` | AI persona ("Emily") turns |
| `role: "user"` | Customer turns |

---

## Issue Taxonomy

Claude scores each conversation against this rubric:

### Categories
`Intent` · `Info Collection` · `Conversation Flow` · `Process Logic` · `Customer Request` · `System Glitch`

### Subtypes
`Phone Pricing` · `Scope Expansion` · `Repetition` · `Skipped Required Info` · `Service Area` · `Callback Handling` · `Duplicate Opportunity` · `Availability Ignored` · `Automation Error` · `Photo Request Handling` · `Customer Data` · `Communication Preference` · `Disposition` · `Misc Awkward`

### Severity
`Critical` · `Medium` · `Mild`

---

## Gotchas

- Apps Script web app must be redeployed (new deployment version) after any code change for the live URL to pick up the update
- The 1-min trigger runs even when there's nothing in the queue — this is fine, it no-ops
- Hatch's `Assistant Conversation Completed` event fires when the AI hands off or the conversation closes; it does NOT fire for human-only exchanges
- Claude's rubric must reference the current chatbot instructions — keep it in sync when PPP updates the bot's script
