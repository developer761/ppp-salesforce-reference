# Service Cloud Voice — what number an outbound call actually presents

Determining which phone number a customer sees when an agent dials out of Service Cloud Voice
(Salesforce + Amazon Connect), and why the obvious places to look are all wrong.

**Sanitized.** Numbers, names, instance/flow ids and bucket names are deliberately absent — they
live in the admin's private working folder.

---

## The rule

Amazon Connect has **no per-agent outbound caller ID setting.** Caller ID is a property of the
STANDARD queue (`OutboundCallerConfig.OutboundCallerIdNumberId`), so by default everyone in a queue
shares one outbound identity.

**But a queue can override it at runtime**, and if it does, nothing in the queue config or in
Salesforce will tell you. The override lives in the queue's **outbound whisper flow**
(`OutboundCallerConfig.OutboundFlowId`, flow type `OUTBOUND_WHISPER`):

```
InvokeLambdaFunction   <lambda>        ──► returns {"phoneNumber": "<E.164>", ...}
CompleteOutboundCall   CallerId.Number = $.External.phoneNumber
```

A `CompleteOutboundCall` action carrying a `CallerId` parameter **replaces** the queue's configured
number for that call. A whisper flow without one falls through to the queue default.

So the first question on any caller-ID investigation is not "what is the queue set to" — it is
**"do all the queues share one outbound flow, and does that flow set a caller ID?"**

```bash
# for each STANDARD queue: is there an OutboundFlowId, and is it the same one everywhere?
aws connect list-queues   --instance-id <id> --queue-types STANDARD
aws connect describe-queue --instance-id <id> --queue-id <qid>
aws connect describe-contact-flow --instance-id <id> --contact-flow-id <fid>   # read Content
```

`list-queues` without `--queue-types STANDARD` also returns **AGENT**-type personal queues. Those
have no outbound caller-ID property, so `describe-queue` failing on them is expected — not a gap in
coverage. Filtering proves it rather than leaving it ambiguous.

---

## 🔴 `VoiceCall.FromPhoneNumber` is NOT the presented caller ID

On an outbound call, Salesforce populates `FromPhoneNumber` with the **queue's configured number**.
When a whisper flow overrides caller ID, `FromPhoneNumber` does not follow. The same is true of
`describe-contact`'s `SystemEndpoint.Address`.

The only field observed to match what the receiving carrier actually saw is the **contact tag**:

```bash
aws connect describe-contact --instance-id <id> --contact-id <VoiceCall.VendorCallKey> \
  --query 'Contact.Tags."aws:connect:systemEndpoint"'
```

| Source | Agrees with the carrier? |
|---|---|
| `describe-queue` → `OutboundCallerIdNumberId` | ❌ queue default, overridable |
| `VoiceCall.FromPhoneNumber` | ❌ mirrors the queue |
| `describe-contact` → `SystemEndpoint.Address` | ❌ mirrors the queue |
| `describe-contact` → `Tags["aws:connect:systemEndpoint"]` | ✅ |

Connect contact records age out at roughly **two years**; older contacts return
`ResourceNotFoundException`, which is retention, not a missing record.

**Consequences for any metric built on `FromPhoneNumber`:** counts of "which of our numbers place
outbound calls", per-number outbound activity, and "this line is inbound-only" verdicts are all
invalid wherever an override exists. Derive them from the contact tag instead.

### Reading direction out of `VoiceCall`

The PPP-side number lives in a different field per direction: inbound → `ToPhoneNumber`,
outbound → `FromPhoneNumber`. Aggregating only one silently hides half the traffic. A few rows
carry an *email address* in `FromPhoneNumber` (softphone-to-softphone legs) — filter them.

### Lambda-driven overrides fail open

A name/key-lookup Lambda returns a `Default` when the key misses. Two ways that happens in practice:

- **No agent leg ever connected** (`AgentInfo` absent on the contact) — the flow has no agent name
  to pass, so the call presents the default. Expect a small tail of these in any sample.
- **The lookup key drifted.** If the map is keyed on the agent's display name, a rename, a rehire,
  or a new joiner silently falls back to the default. Such a map rots with every staffing change
  and usually has no owner and no alerting. **Check its last-modified date** — it is the cheapest
  signal of how stale the mapping is.

An override map keyed on a human-readable name will also happily point two people at the same
number. Diff the map's values against its keys before trusting it.

---

## Two failure modes that produced a confidently wrong answer

Worth stating plainly, because both looked like diligence at the time.

**1. Two "independent" verifications that shared one source.** Queue config and 90 days of
`VoiceCall.FromPhoneNumber` agreed 1:1 — *because the telephony integration copies the queue config
into that field*. Agreement between a configuration and a system that reads that configuration is
not corroboration, no matter how large the sample. Before calling two checks independent, name the
upstream each one actually reads.

**2. A null result with no positive control.** A sweep of two years and ~53,000 inbound calls on a
second phone platform found zero instances of the numbers in question appearing as caller ID, and
that read as confirmation. In fact **no agent holding one of those numbers had ever called that
platform inside the window** — the test had no power to detect the thing it was used to rule out.
Always ask: *if the hypothesis were true, would this test have produced a different result?*

**What settled it: a receiving network the org does not control.** An agent called a line on a
different phone platform; that platform's carrier-delivered caller ID was recorded, with no contact
match to confuse it, and matched the Salesforce record to within seconds. When two internal systems
disagree about what went out on the wire, the answer is on the wire — get a measurement from the
far end.

### Same-day verification trap

Async "stats export" style endpoints on phone platforms commonly lag several hours. An export
requested for "the last 2 days" can silently end at the previous evening, which reads exactly like
*the call never happened*. For same-day checks use the live call-log endpoint with a
`started_after` timestamp, and always check the returned date range rather than the row count.

---

---

## Two more fields that do not mean what their name implies

Found while tracing inbound routing on the same instance. Both are the *same class of error* as
`FromPhoneNumber` above — a field that looks authoritative and is actually a label.

### An IVR-type attribute is a reporting label, not a routing decision

The inbound flow stamps a custom attribute per menu digit (`NewLead` / `ExistingLead` /
`AccountManager` / `Spanish`) and writes it onto the Salesforce call record. It is natural to read
those values as *where the call went*. They are not. In this org, **digits 1, 2 and 3 all set the
same target queue**; the attribute differs, the destination does not.

So an "account manager" menu option can land in exactly the same general queue as "new lead", and
every report grouping on that attribute will faithfully show three distinct intents being handled —
while the routing behind them is identical.

**How to apply:** to learn where a menu option goes, read the `UpdateContactTargetQueue` (or
`TransferContactToQueue` / `TransferToFlow`) on that digit's branch. Never infer routing from an
attribute the flow sets alongside it. And when told "option N goes to team X", check whether the
flow agrees — a recorded menu can keep promising a destination years after the routing changed.

### A queue-name field may mirror the telephony platform, not Salesforce

`VoiceCall.QueueName` carries the **Amazon Connect** queue names, not the Salesforce queue names.
Where the two systems have near-duplicate names (`Account Manager` vs `Account Manager Queue`,
`Inbound Queue` vs `Inbound Calls`), it is easy to join or filter on the wrong one and get a clean,
empty, wrong answer. **Do not join Connect and Salesforce queues on name**, and check which
platform's vocabulary a field speaks before filtering on it.

### Corollary: a queue can be alive for one direction and dead for the other

A queue here shows ~26,000 outbound calls and **zero inbound since a hard cutover two and a half
years ago** — it survives only to carry the outbound caller-ID override. Meanwhile its Salesforce
counterpart is correctly staffed, and nothing routes inbound work to it. An inbound flow still
targets it and has therefore not executed since.

**How to apply:** when asked whether a queue is in use, split the answer by direction and give the
date of the last call in each. "In use" hides a queue that is half dead, and a flow that targets a
queue receiving no inbound is strong evidence **no number points at that flow any more** — which is
checkable, because Connect exposes no number-to-flow association API.

## Checklist for "what number did the customer see?"

1. Get the contact id — `VoiceCall.VendorCallKey`.
2. Read `Tags["aws:connect:systemEndpoint"]` off `describe-contact`. That is the answer.
3. Only then, to explain *why*: check the queue's `OutboundFlowId`, read the flow's `Content`,
   and look for a `CompleteOutboundCall` carrying a `CallerId` parameter.
4. If a Lambda feeds it, find where its map lives and when it was last modified.
5. Never quote `FromPhoneNumber` as the presented number.
