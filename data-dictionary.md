# T21 Clinical Decision Support — Data Dictionary

This document describes every ActivityDefinition and PlanDefinition in the system, including timing windows, applicability conditions, recurrence rules, and the codes used for fulfillment matching.

---

## Activity Definitions

Each ActivityDefinition represents a single orderable clinical action. The `code` field is used to match against Observations, Procedures, or Encounters when checking whether a ServiceRequest has been fulfilled.

| ID | Title | Code System | Code | Display | Fulfillment Type |
|----|-------|-------------|------|---------|-----------------|
| t21-tsh-screening | TSH Screening | LOINC | 11580-8 | Thyrotropin [Units/volume] in Serum or Plasma | Observation |
| t21-antithyroid-antibody-measurement | Anti-Thyroid Antibody Measurement | LOINC | 8099-4 | Thyroperoxidase Ab [Units/volume] in Serum or Plasma | Observation |
| t21-karyotype-analysis | Karyotype Analysis | SNOMED | 117010004 | Chromosomal karyotype determination | Observation |
| t21-cbc | Complete Blood Count (CBC) | LOINC | 58410-2 | CBC panel - Blood by Automated count | Observation |
| t21-tte-echocardiogram | Transthoracic Echocardiogram | LOINC | 34552-0 | 2D echocardiogram panel | Procedure |
| t21-hearing-assessment | Objective Hearing Assessment | LOINC | 32437-6 | Audiology study | Observation/Procedure |
| t21-feeding-assessment | Feeding Assessment | SNOMED | 710849003 | Assessment of feeding | Procedure |
| t21-ophthalmology-referral | Ophthalmology Referral | SNOMED | 183524004 | Referral to ophthalmology service | Encounter |
| t21-early-intervention-referral | Early Intervention Referral | SNOMED | 306206005 | Referral to rehabilitation service | Encounter |

---

## Plan Definitions

Each PlanDefinition groups one or more actions that define when and under what conditions a screening or referral should be ordered.

---

### 1. TSH Screening Schedule

**PlanDefinition ID:** aap-t21-tsh-schedule

Thyroid function screening with cadence that depends on anti-thyroid antibody status.

| Action ID | Title | Timing | Recurrence | Condition |
|-----------|-------|--------|------------|-----------|
| newborn-tsh | Newborn TSH Screen | 0–1 months from DOB | None | None |
| six-month-tsh | 6-Month TSH Screen | 5–7 months after newborn-tsh | None | None |
| annual-tsh | Annual TSH Screen | 11–13 months after newborn-tsh | Every 11–13 months through age 21 | No positive anti-thyroid antibody result |
| semiannual-tsh | Semi-Annual TSH Screen (Antibody Positive) | 5–7 months after newborn-tsh | Every 5–7 months through age 21 | Positive anti-thyroid antibody result exists |

**Condition details:**

The annual and semi-annual actions are mutually exclusive based on anti-thyroid antibody status:

- **Annual (no antibodies):** `%observations.where(code.coding.where(system='http://loinc.org' and code='8099-4').exists() and (valueQuantity.value > 9.0 or interpretation.coding.where(code='POS').exists())).empty()` — fires when no positive antibody result (LOINC 8099-4 with value > 9.0 IU/mL or POS interpretation) exists.

- **Semi-annual (antibodies detected):** `%observations.where(code.coding.where(system='http://loinc.org' and code='8099-4').exists() and (valueQuantity.value > 9.0 or interpretation.coding.where(code='POS').exists())).exists()` — fires when a positive antibody result is present.

---

### 2. Anti-Thyroid Antibody Screening Schedule

**PlanDefinition ID:** aap-t21-antithyroid-antibody-schedule

One-time antibody screen in the first year. A positive result changes TSH cadence from annual to semi-annual.

| Action ID | Title | Timing | Recurrence | Condition |
|-----------|-------|--------|------------|-----------|
| first-year-antithyroid-antibody | First-Year Anti-Thyroid Antibody Screen | 0–12 months from DOB | None | No prior antibody result on file |

**Condition:** `%observations.where(code.coding.where(system='http://loinc.org' and code='8099-4').exists()).empty()` — suppressed if any anti-thyroid antibody observation (LOINC 8099-4) already exists, regardless of value.

---

### 3. Karyotype Confirmation Schedule

**PlanDefinition ID:** aap-t21-karyotype-schedule

One-time karyotype to confirm T21 diagnosis. Ideally performed prenatally.

| Action ID | Title | Timing | Recurrence | Condition |
|-----------|-------|--------|------------|-----------|
| confirmatory-karyotype | Confirmatory Karyotype Analysis | -9 to 0 months from DOB (prenatal) | None | No positive T21 karyotype on file |

**Condition:** `%observations.where(code.coding.where(system='http://loinc.org' and code='29770-5').exists() and valueCodeableConcept.coding.where(system='http://snomed.info/sct' and code='41040004').exists()).empty()` — suppressed if a karyotype observation (LOINC 29770-5) with a value of Complete trisomy 21 syndrome (SNOMED 41040004) already exists.

---

### 4. CBC Schedule

**PlanDefinition ID:** aap-t21-cbc-schedule

Initial CBC at birth plus annual monitoring for hematologic abnormalities (TAM, leukemia).

| Action ID | Title | Timing | Recurrence | Condition |
|-----------|-------|--------|------------|-----------|
| newborn-cbc | Newborn CBC | 0–1 months from DOB | None | None |
| annual-cbc | Annual CBC | 11–13 months after newborn-cbc | Every 11–13 months through age 21 | None |

---

### 5. TTE Echocardiogram Schedule

**PlanDefinition ID:** aap-t21-tte-schedule

One-time echocardiogram to evaluate for congenital heart defects.

| Action ID | Title | Timing | Recurrence | Condition |
|-----------|-------|--------|------------|-----------|
| newborn-tte | Newborn TTE | 0–1 months from DOB | None | None |

---

### 6. Hearing Assessment Schedule

**PlanDefinition ID:** aap-t21-hearing-assessment-schedule

Objective hearing assessment (ABR or OAE) in the first 6 months.

| Action ID | Title | Timing | Recurrence | Condition |
|-----------|-------|--------|------------|-----------|
| newborn-hearing-assessment | Newborn Hearing Assessment | 0–6 months from DOB | None | None |

---

### 7. Feeding Assessment Schedule

**PlanDefinition ID:** aap-t21-feeding-assessment-schedule

Condition-triggered feeding assessment with no specific time window. Generates a ServiceRequest immediately when clinical criteria are met.

| Action ID | Title | Timing | Recurrence | Condition |
|-----------|-------|--------|------------|-----------|
| feeding-assessment-triggered | Feeding Assessment / Video Swallow Study | Any time (condition-only) | None | Hypotonia or underweight documented |

**Condition:** `%observations.where(code.coding.where(system='http://snomed.info/sct' and code='398152000').exists()).exists() or %observations.where(code.coding.where(system='http://loinc.org' and code='77606-2').exists() and valueQuantity.value < 5).exists() or %observations.where(code.coding.where(system='http://loinc.org' and code='59576-9').exists() and valueQuantity.value < 5).exists()`

Triggers when any of the following are present:

- Marked hypotonia (SNOMED 398152000)
- Weight-for-length percentile < 5th (LOINC 77606-2 with value < 5)
- BMI percentile < 5th (LOINC 59576-9 with value < 5)

---

### 8. Ophthalmology Referral Schedule

**PlanDefinition ID:** aap-t21-ophthalmology-referral-schedule

Referral to ophthalmology for screening of cataracts, strabismus, nystagmus, and refractive errors.

| Action ID | Title | Timing | Recurrence | Condition |
|-----------|-------|--------|------------|-----------|
| infant-ophthalmology-referral | Infant Ophthalmology Referral | 0–6 months from DOB | None | None |

---

### 9. Early Intervention Referral Schedule

**PlanDefinition ID:** aap-t21-early-intervention-referral-schedule

Referral to early intervention for speech, fine motor, or gross motor therapy.

| Action ID | Title | Timing | Recurrence | Condition |
|-----------|-------|--------|------------|-----------|
| early-intervention-referral | Early Intervention Referral | 0–36 months from DOB | None | None |

---

## Fulfillment Logic

A ServiceRequest is suppressed (not generated) when matching clinical data already exists for its time window.

The system checks three resource types for fulfillment:

- **Observations** — matched by code on `Observation.code.coding` and date on `Observation.effectiveDateTime`
- **Procedures** — matched by code on `Procedure.code.coding` and date on `Procedure.occurrenceDateTime` or `Procedure.occurrencePeriod.start`
- **Encounters** — matched by code on `Encounter.type.coding` and date on `Encounter.actualPeriod.start`

For time-windowed actions, the fulfillment must fall within the scheduled window. For condition-only actions (no time window), any matching resource at any date counts.

---

## Overdue Flags

When a ServiceRequest's scheduled window has passed and no fulfillment exists, a FHIR Flag resource is generated:

- **Code:** SNOMED 441586009 (Overdue for screening)
- **Category:** Administrative
- **Period start:** end date of the missed window
- **Extension:** links to the triggering ServiceRequest via `https://t21app.example.org/fhir/StructureDefinition/flag-triggering-resource`

---

## Persistence and Reconciliation

ServiceRequests are persisted to disk in each patient's `service-requests/` directory. On each run:

1. `apply_plan` determines what SRs should exist (stateless, based on current clinical data)
2. `reconcile_service_requests` compares against what's on disk:
   - New SRs (generated but not on disk) are written as `active`
   - Fulfilled SRs (on disk but no longer generated) are updated to `completed`
   - Existing active SRs that were regenerated are left unchanged

---

## Code Systems Reference

| System | URL | Used For |
|--------|-----|----------|
| LOINC | http://loinc.org | Lab tests, panels, assessments |
| SNOMED CT | http://snomed.info/sct | Clinical findings, procedures, referrals |
| UCUM | http://unitsofmeasure.org | Units of measure (months, percentiles) |
| HL7 Flag Category | http://terminology.hl7.org/CodeSystem/flag-category | Flag categorization |
| HL7 Plan Definition Type | http://terminology.hl7.org/CodeSystem/plan-definition-type | PlanDefinition type (protocol) |
| HL7 v3 ActCode | http://terminology.hl7.org/CodeSystem/v3-ActCode | Encounter class (AMB) |
