# FHIR Activity Plan Engine

A small Python engine that turns FHIR `PlanDefinition` and `ActivityDefinition` resources into patient-specific `ServiceRequest` orders, overdue `Flag` resources, and a self-contained HTML timeline dashboard. The engine itself is generic — no clinical logic is baked in. The shipped artifact library implements the **AAP Trisomy 21 (Down syndrome) screening guidelines** as a worked example.

## What the engine does

Given:

- a library of `PlanDefinition` resources (screening protocols)
- a library of `ActivityDefinition` resources (orderable actions)
- a patient with their `Observation` / `Procedure` / `Encounter` history

The engine produces:

- `ServiceRequest` resources for screenings due now
- `Flag` resources for windows that have already passed without fulfillment
- a `debug_timeline.html` **dashboard** that visualizes the entire reasoning trace on a single chronological axis

It runs stateless on each invocation — what should exist is recomputed from scratch every time. Reconciliation against persisted state happens only at write time, so updating an artifact or correcting a bad observation takes effect on the very next run with no migration step.

## Why the engine is interesting

Most CDS implementations hard-code clinical rules in application code. This one keeps every rule out of the engine — timing windows, recurrence cadences, applicability conditions, and code matchers all live in **versioned FHIR knowledge artifacts** under `fixtures/`. The engine is generic; it only knows how to read FHIR.

In practice that means three things:

The rules are **diffable**. Updating "annual TSH" to "every 9 months for antibody-positive patients" is a JSON edit, reviewable in a PR, with no engine changes.

The rules are **portable**. The same engine should run any guideline set — primary care wellness, oncology surveillance, pre-op workup — by swapping the artifact library. The T21 library is one example; the engine doesn't know it's T21.

The rules are **auditable**. Every generated `ServiceRequest` traces back to the canonical URL of the `ActivityDefinition` and `PlanDefinition` that produced it.

## How an artifact becomes an order

A simplified view of the TSH screening plan in the example library:

```
PlanDefinition: aap-t21-tsh-schedule
  action: annual-tsh
    definitionCanonical → ActivityDefinition: t21-tsh-screening (LOINC 11580-8)
    timingTiming: every 11–13 months through age 21
    condition (FHIRPath):
      no positive anti-thyroid antibody result exists
```

For a 4-year-old patient with no antibody-positive observations, the engine:

1. Resolves the timing windows from DOB
2. Evaluates the FHIRPath condition against the patient's observations (passes)
3. For each window, checks whether a matching `Observation` (LOINC 11580-8) already exists in that window
4. Generates a `ServiceRequest` for any unfulfilled window
5. Generates an overdue `Flag` for any window whose end date has passed

## The deliverable: the timeline dashboard

`debug_timeline.py` is the primary deliverable. It runs the engine end-to-end for a single patient and emits a self-contained `debug_timeline.html` — a chronological dashboard showing:

- every scheduled window for every action
- every fulfilling `Observation` / `Procedure` / `Encounter` overlaid on those windows
- every generated `ServiceRequest` (active, completed, overdue)
- every overdue `Flag`

It's a single HTML file with no server, no build step, and no external dependencies — open it in a browser. It's the fastest way to see whether the engine is doing what you expect when an artifact changes, and the simplest way to demo the pipeline to someone who doesn't want to read JSON.

## The shipped example library: AAP Trisomy 21 screening

`fixtures/` contains 9 `ActivityDefinition` and 9 `PlanDefinition` resources implementing the American Academy of Pediatrics screening recommendations for patients with Down syndrome:

- TSH screening (newborn → 6mo → annual or semi-annual depending on antibody status)
- Anti-thyroid antibody one-time screen
- Confirmatory karyotype (prenatal)
- CBC (newborn + annual through age 21)
- Transthoracic echocardiogram (newborn)
- Newborn hearing assessment
- Feeding assessment (condition-triggered: hypotonia or low weight-for-length)
- Infant ophthalmology referral
- Early intervention referral

The library is the example, not the point. Replace `fixtures/` and `patients/` with another guideline set and patient cohort, and the engine should run unchanged.

## Quickstart

```bash
pip install fhir.resources fhirpathpy python-dateutil

# Run the engine and emit the dashboard for one patient
python debug_timeline.py patients/patient-1
# Then open debug_timeline.html in a browser

# Or run the engine directly and print to stdout
python logic.py patients/patient-1
```

## Project layout

```
fixtures/
  activity-definitions/     # 9 orderable actions (T21 example)
  plan-definitions/         # 9 screening protocols (T21 example)
patients/
  patient-{1,2,3}/          # example patients with observations, procedures, encounters
logic.py                    # the engine: load_fixtures, apply_plan, reconcile_service_requests
debug_timeline.py           # generates the HTML dashboard deliverable
```

## Tech stack

Python 3.10+, [`fhir.resources`](https://github.com/nazrulworld/fhir.resources) for typed FHIR R5 models, [`fhirpathpy`](https://github.com/beda-software/fhirpath-py) for FHIRPath evaluation, and `python-dateutil` for relative date arithmetic. The dashboard is a single HTML file generated by Python — no JS build step, no framework.

## Status

Teaching / portfolio project. Complete enough to demonstrate the artifact-driven CDS pattern end-to-end, but not intended for clinical use — the artifact library is illustrative, the FHIRPath conditions are simplified, and there's no security model.

## License

MIT (or whatever you prefer — add a LICENSE file).
