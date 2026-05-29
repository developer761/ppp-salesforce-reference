# Paint Gallons Calculator — Estimating Logic

Standard logic for auto-suggesting a paint **order quantity (gallons)** for a job, so a
project manager doesn't have to estimate from experience. Built for PPP's calculator tool.

This is a **suggested order**, not a precise takeoff. Every space differs; the goal is a
defensible default a PM can trust and adjust. Inputs are used **when available**, otherwise
sensible defaults fill in (there is no system that forces PMs to capture door/window/closet
counts).

> Status: spec locked 2026-05-29. Coverage rate and buffer are deliberately a little
> generous — PPP would rather leave touch-up cans with the client than send a crew back
> mid-job for more paint.

---

## Output: three numbers per job, by color + finish

A job produces **three independent results**, each rolled up by `color + finish + product`:

| Bucket | Product / finish | Notes |
|---|---|---|
| **Ceiling** | flat | usually white |
| **Walls** | wall color | the room's wall color |
| **Trim** | the **wall paint line in a semi-gloss finish** | often white; sometimes BM Advance for a more enamel-like finish. PPP does *not* use a dedicated trim enamel by default. **Door faces (when in scope) use this trim paint/finish.** |

Brands: **Benjamin Moore** primarily — Ultra Spec (contractor line) or Regal; trim sometimes
BM Advance. **Sherwin Williams** more for commercial work and in FL / TX / CA / CO. Coverage
rate should be a **configurable constant per product/finish** so these can be tuned without
changing the formulas.

---

## Constants

| Item | Value | Notes |
|---|---|---|
| Coats | **2** | all surfaces |
| Coverage rate | **375 sq ft / gallon** | configurable per product/finish; default 375 |
| Buffer | **+10%** | applied per color/finish at the job level, after roll-up |
| Default openings (when counts not captured) | **1 door + 1 window per room**, 0 closets | closets counted only when entered (bedrooms / foyers) |
| **Wall deductions** (per opening) | | subtracted from wall area |
| &nbsp;&nbsp;Door | 20 sq ft | 3'0" × 6'8" |
| &nbsp;&nbsp;Window | 15 sq ft | avg residential |
| &nbsp;&nbsp;Closet | 30 sq ft | ~5' bifold |
| **Trim additions** (per opening, casing) | | added to trim linear feet |
| &nbsp;&nbsp;Door casing | 17 LF | 2 legs + head (no bottom) |
| &nbsp;&nbsp;Window casing | 15 LF | 4-sided |
| &nbsp;&nbsp;Closet casing | 18 LF | 2 legs + head |
| Trim width (LF → sq ft) | **× 0.25 ft** (3") | converts linear feet of trim to paintable sq ft |
| Door face (when in scope) | **20 sq ft each, single-sided** | trim paint/finish; count = WorkOrder `Doors`; only if scope includes painting doors |

Baseboard interruption at doors/closets is intentionally **ignored** (minor; leans slightly
generous).

---

## Per-room formulas (2-coat coverage, in sq ft)

Inputs per room: width `W`, length `L`, height `H` (ft); counts of doors / windows / closets;
whether door faces are in scope.

```
ceiling_sqft = (W * L) * 2

wall_sqft    = ( (2*W + 2*L) * H
                 - doors   * 20
                 - windows * 15
                 - closets * 30 ) * 2

perimeter_lf = 2*W + 2*L
trim_lf      = perimeter_lf + doors*17 + windows*15 + closets*18
trim_sqft    = (trim_lf * 0.25) * 2
               + (paint_door_faces ? doors * 20 * 2 : 0)
```

Tag each result with its `color + finish + product` so it can be summed across rooms.

---

## Roll-up → suggested order (per color/finish, whole job)

Customers often use the same color in multiple rooms, so combine and round **once** at the
job level — not per room.

```
for each (color, finish):
    total_sqft = sum of that surface's 2-coat sqft across all rooms
    gallons    = total_sqft / coverage_rate          # 375 default
    gallons    = gallons * 1.10                       # +10% buffer

    # packaging: individual gallons up to 4; switch to 5-gal buckets above 4
    buckets = 0
    while gallons > 4:
        buckets += 1
        gallons -= 5
    cans = ceil(max(gallons, 0))                       # leftover one-gallon cans
    order = { buckets: buckets (×5 gal), cans: cans }
```

Packaging examples (post-buffer gallons → order):
`3.0 → 3 cans` · `4.0 → 4 cans` · `4.5 → 1 bucket` · `6.2 → 1 bucket + 2 cans` ·
`9.5 → 2 buckets` · `14 → 2 buckets + 4 cans`.

Minimum one gallon per color/finish that has any coverage.

---

## Worked example — one 12 × 12 × 8 ft bedroom

Openings: 1 door (face painted), 2 windows, 1 closet. Coverage 375, +10%.

| Surface | Coverage sq ft (2 coats) | ÷375 | ×1.10 | Order (1-room job) |
|---|---|---|---|---|
| Ceiling | 144 × 2 = 288 | 0.77 | 0.84 | **1 gal** |
| Walls | (384 − 20 − 30 − 30) × 2 = 608 | 1.62 | 1.78 | **2 gal** |
| Trim | (48+17+30+18)·0.25·2 = 56.5  +  door face 1·20·2 = 40  →  96.5 | 0.26 | 0.28 | **1 gal** |

On a real multi-room job, sum each color's coverage sq ft across all rooms *before* the
÷375 / ×1.10 / packaging step.

---

## Implementation notes for the calculator

- Treat **coverage rate, buffer %, the deduction/casing constants, and trim width** as named
  config values, not magic numbers — PPP will tune them (e.g. per product or per SW vs. BM).
- Accept actual door/window/closet counts per room; fall back to the defaults above when a
  count is blank.
- "Paint door faces" is a per-job (or per-room) scope flag, default off, driven by the
  WorkOrder scope; the door count it uses is the same `Doors` value.
- Output should name the **product line + finish** alongside gallons (e.g. "Walls — BM Regal,
  eggshell, [color]: 1 bucket + 2 gal") so purchasing knows exactly what to buy.
