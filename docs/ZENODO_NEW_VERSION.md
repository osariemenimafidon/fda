# Publishing the corrected Atlas preprint as a new Zenodo version

Written 2026-09-18, against repository commit `35a9aa1`.

## Why a new version rather than a new record or a deletion

`10.5281/zenodo.22822535` already exists publicly and resolves to the **pre-correction**
manuscript — the one that carried cetane ceilings of 80 and 56, which no standard states,
and that reported a finite cetane sensitivity band where 98.6% of state-years actually have
no finite upper bound.

Three things follow.

**Do not delete it.** Zenodo does not let a depositor delete a published record, and that
is the correct behaviour: a DOI is a promise that a citation keeps resolving. Someone may
already have the old link.

**Do not create a separate new record.** That would leave two unconnected DOIs for the same
paper, and no reader arriving at the old one would learn that a corrected version exists.

**Publish a new version of the existing record.** Zenodo keeps both, marks the old one as
superseded, and the *concept* DOI — `22822535`, the one without a version — resolves to the
newest. Anyone citing it lands on the corrected paper. The old version DOI keeps working
for anyone who cited it specifically, which is what makes this honest rather than a
cover-up.

---

## The steps

### 1. Open the record

Go to **https://doi.org/10.5281/zenodo.22822535**

It redirects to the version record `22822536`. Sign in if you are not already.

### 2. Click "New version"

The button is on the right-hand side of the record page, under the file list. It creates an
unpublished draft that inherits all the existing metadata — you only change what differs.

> If you do not see the button, you are not signed in as the record's owner. Sign in and
> reload before doing anything else.

### 3. Replace the file

Delete the existing `FDA_preprint.pdf` from the draft's file list, then upload the current
one:

- **File:** `~/Documents/fda/docs/FDA_preprint.pdf`
- **Size:** 379,211 bytes
- **Built:** 2026-09-18 from commit `35a9aa1`

Zenodo will not let you publish a new version that has exactly the same files as the last
one, so replacing the PDF is what makes this a real version rather than a metadata edit.

### 4. Set the version number

Change the **Version** field from `v1` to:

```
v2
```

### 5. Add the version notes

Zenodo has no dedicated "changes" field, so this goes at the **top of the Description**,
above the existing abstract text. Paste it exactly:

> **Version 2 (18 September 2026) — corrected.** Version 1 carried cetane maxima of 80
> (HVO) and 56 (FAME). Neither is a specification value: EN 15940, EN 14214 and ASTM D6751
> all state cetane minima and no maximum. Those invented ceilings closed the sensitivity
> interval and understated the uncertainty on every cetane result; 98.6% of state-years in
> fact have no finite upper bound on their cetane deviation. This version separates what a
> standard guarantees from what the study assumes, withdraws the cetane point estimate in
> favour of a specification-derived bound, and retires the divergence index. It also
> replaces the assumed FAME density on the critical path with a breakdown point, reports
> the 91.9% nonroad composition of the companion certification panel as a limit on scope,
> and passes a verification gate whose mechanical half is evidenced in `qa/` rather than
> attested. No density estimate changed: the 38.3 kg/m³ spread, the 3/40/8 split and
> California at 54.6% non-petroleum and −34.1 kg/m³ are identical to version 1.

### 6. Check these fields carried over

They should have inherited, but confirm before publishing:

| Field | Value |
|---|---|
| Title | How far has the diesel pool moved from the certification fuel? A state-level specification-based atlas for the United States, 2011–2024 |
| Resource type | Preprint |
| Author | Imafidon, Osariemen — ORCID 0009-0006-3069-4674 |
| Licence | Creative Commons Attribution 4.0 International |
| Related identifier | https://github.com/osariemenimafidon/fda |

If the related identifier is missing, add it with relation **"is supplement to"**.

### 7. Publish

Click **Publish**. Confirm when asked.

### 8. Check it worked

- **https://doi.org/10.5281/zenodo.22822535** should now land on v2.
- The old version DOI `…22822536` should still resolve, and should show a banner saying a
  newer version exists.
- Send me the new version DOI and I will record it in the portfolio, the evidence log and
  your CV.

---

## Separately: the GitHub release may have minted its own DOI

The `v1.0.0` release cut today is a different object — the dataset and pipeline, not the
manuscript. Check **https://zenodo.org/account/settings/github/**:

- If `fda` is switched **on**, a DOI badge will have appeared and that deposit happened
  automatically. It is correct for it to be separate: a dataset DOI and a preprint DOI
  describe different things and both should exist.
- If `fda` is switched **off**, no deposit happened. Turn it on, then cut a `v1.0.1`
  release — Zenodo only archives releases published *after* the switch is on, so the
  existing `v1.0.0` will not be picked up retroactively.

Send me whichever DOIs appear and I will wire them in.
