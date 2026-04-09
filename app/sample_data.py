"""
sample_data.py
--------------
Provides the patient's clinical events and problem list for development
and demonstration purposes.

To swap in real data later, replace load_sample_events() with a function
that reads from a database, EHR API, or CSV — the rest of the app doesn't
need to change as long as the function returns a list of ClinicalEvent objects.

Linking encounters, diagnoses, and labs
----------------------------------------
  - Each Diagnosis and Lab carries a `linked_encounter` field naming the
    Encounter where it was addressed / ordered. This lets the timeline popup
    for an encounter show what happened during that visit.

  - Each Lab also carries a `linked_diagnosis` field naming the Diagnosis it
    relates to. This feeds the problem list's "Details" cross-reference.

  - Use the exact label string from the matching encounter() / diagnosis()
    call as the link value. The frontend does a simple string match.

Key Python concepts used in this file
--------------------------------------
This file demonstrates several important Python features that a beginner
should understand:

1. FUNCTIONS THAT RETURN LISTS:
   load_sample_events() is a function that returns a list. The `return`
   keyword passes the entire list back to the caller. This is a fundamental
   pattern in Python: functions that gather data and return it as a collection.

2. DATE OBJECTS:
   We use `date(2024, 3, 15)` to create a date object representing a specific
   calendar date (March 15, 2024). This is imported from Python's datetime
   module and lets us work with dates consistently across the application.

3. KEYWORD ARGUMENTS:
   When we call diagnosis(..., status="active", icd10="Q90.0", ...), the
   parts after the function label and description are keyword arguments.
   They have names (like "status") and values (like "active"). Using keyword
   arguments makes the code self-documenting — you can read what each value
   means without looking at the function definition.

4. LIST COMPREHENSIONS WITH FILTERING:
   The line:
     [problem(...) for ev in load_sample_events() if ev.category == Category.DIAGNOSIS]
   is a list comprehension. It's a concise way to build a new list by:
     - Looping through events: `for ev in load_sample_events()`
     - Filtering them: `if ev.category == Category.DIAGNOSIS`
     - Transforming each one: `problem(...)`
   This replaces what would otherwise be a multi-line for loop.
"""

from datetime import date

# Import all constructor functions from models.
# Each one creates a ClinicalEvent of the appropriate category:
#   - date: A class that represents a specific calendar date (e.g., March 15, 2024).
#     Calling date(2024, 3, 15) creates the date object for that exact day.
#
#   - Category: An enumeration (list of named choices) used to tag events by type.
#     Category.DIAGNOSIS, Category.LAB, Category.ENCOUNTER, etc. are the choices.
#
#   - diagnosis(): Constructor that creates a diagnosis event. Takes a label,
#     date, and optional keyword args like status, icd10, linked_encounter.
#
#   - encounter(): Constructor that creates an encounter (doctor visit) event.
#     Takes a label, date, description, and optional keyword args like provider,
#     location, and planned.
#
#   - lab(): Constructor that creates a lab/investigation result event.
#     Takes a label, date, and optional keyword args like linked_encounter,
#     linked_diagnosis, result, and planned.
#
#   - counseling(): Constructor that creates a counseling/educational event
#     (a subtype of therapeutic intervention). Takes a label, date, and optional
#     keyword args like linked_encounter, provider, and planned.
#
#   - medication(): Constructor that creates a medication event (drug start/change).
#     Takes a label, date, and optional keyword args like linked_encounter,
#     linked_diagnosis, dose, frequency, and planned.
#
#   - problem(): Constructor that creates a Problem object for the problem list.
#     Takes name, onset_date, status, icd10, and description.
from models import Category, diagnosis, encounter, lab, counseling, medication, problem


# ---------------------------------------------------------------------------
# load_sample_events
# ---------------------------------------------------------------------------

def load_sample_events():
    """
    Return the full list of clinical events for the patient.

    BIG PICTURE:
    This function returns ALL the clinical events (both past and future) for
    this one patient. In a real application, this would query a database or
    call an EHR API. For now, we're using hardcoded sample data to demonstrate
    the application.

    Events are grouped here by type (diagnoses, labs, encounters, therapeutics)
    purely for human readability while writing and reviewing the code. The order
    in which they appear in this list does NOT matter to the timeline — the
    frontend sorts all events by date automatically. So even though we write
    diagnoses first, then labs, then encounters, the timeline might display
    an encounter, then a lab, then a diagnosis, depending on their dates.

    Data model summary:
    - Encounters are the "anchor" events: doctor visits, hospital admissions,
      surgery, etc. Other events link TO encounters.
    - Diagnoses are medical conditions (e.g., "Trisomy 21", "Hypothyroidism").
    - Labs are investigations and test results (e.g., blood tests, imaging).
    - Therapeutics cover two subtypes: counseling (education, therapy referrals)
      and medications (drug starts, dose changes, discontinuations).
    - Each Diagnosis, Lab, or medication event can carry a linked_encounter
      field, which is the label of the encounter it belongs to. This is used
      to show "what happened at this visit?"
    - Each Lab can also carry a linked_diagnosis field, used by the problem
      list to cross-reference labs to the problems they investigate.
    """
    return [

        # ── DIAGNOSES ──────────────────────────────────────────────────────
        # WHAT IS A DIAGNOSIS?
        # A diagnosis is a medical condition or disease that a patient has or
        # had. In clinical practice, diagnoses are recorded to document the
        # patient's health issues. Each diagnosis in this file includes:
        #
        #   label: The name of the condition (e.g., "Trisomy 21")
        #
        #   event_date: When the diagnosis was made or became known. For
        #              Trisomy 21 diagnosed at birth, that's the birth date.
        #
        #   description: A note explaining how it was discovered, what findings
        #               led to the diagnosis (e.g., "Confirmed via karyotype").
        #
        #   status: Either "active" (the patient still has this problem) or
        #          "resolved" (the problem was fixed or went away). This field
        #          appears in the problem list so clinicians know which issues
        #          are current and which are closed. Examples:
        #          - "Trisomy 21" is "active" because the patient will always
        #            have trisomy 21.
        #          - "Complete AVSD" is marked "resolved" after surgery fixed it.
        #
        #   icd10: A standardized code used worldwide for billing and medical
        #         record-keeping. ICD-10 codes are assigned by the World Health
        #         Organization. For example, Q90.0 is the ICD-10 code for Trisomy
        #         21 (Down syndrome). Doctors use these codes for:
        #         - Insurance billing (so the insurance company knows what was
        #           treated)
        #         - Research (analyzing trends across many patients)
        #         - Electronic health records (a standard way to record diagnoses)
        #
        #   linked_encounter: The label of the Encounter event at which this
        #                     diagnosis was made or addressed. For example, the
        #                     "Trisomy 21" diagnosis links to "Birth / NICU Admission"
        #                     because that's when it was confirmed. When the user
        #                     clicks on that encounter in the timeline, the app will
        #                     show all diagnoses linked to it.

        diagnosis(
            "Trisomy 21",
            date(2024, 3, 15),
            "Confirmed via karyotype at birth",
            status="active",
            icd10="Q90.0",
            linked_encounter="Birth / NICU Admission",
        ),

        diagnosis(
            "Complete AVSD",
            date(2024, 4, 2),
            "Complete atrioventricular septal defect identified on echocardiogram",
            status="resolved",
            icd10="Q21.2",
            linked_encounter="Cardiology Consult",
        ),

        diagnosis(
            "Hypothyroidism",
            date(2024, 9, 10),
            "Elevated TSH on routine screening",
            status="active",
            icd10="E03.9",
            linked_encounter="Genetics Follow-up",
        ),


        # ── LABS / INVESTIGATIONS ──────────────────────────────────────────
        # WHAT ARE LABS?
        # Labs are investigations: blood tests, imaging (X-rays, ultrasound,
        # echocardiograms), and other diagnostic procedures ordered by doctors
        # to learn more about a patient's condition. Lab results give objective
        # data: "What does the blood test show? What does the ultrasound reveal?"
        #
        # WHY DO LABS LINK TO BOTH ENCOUNTERS AND DIAGNOSES?
        # - linked_encounter: The visit at which the lab was ordered. For
        #   example, the echocardiogram was ordered during the "Cardiology Consult"
        #   encounter. This connection lets the timeline show "During this visit,
        #   we ordered these tests."
        # - linked_diagnosis: The medical problem that prompted this test. The
        #   echocardiogram was done to investigate suspected heart defects (which
        #   became the "Complete AVSD" diagnosis). This connection helps the
        #   problem list show: "For this problem, here are the tests we ran and
        #   their results."
        #
        # Each lab event includes:
        #   label: The name of the test (e.g., "Complete Blood Count")
        #   event_date: When the test was performed
        #   description: Context about why it was done or notable findings
        #   linked_encounter: The encounter label during which this was ordered
        #   linked_diagnosis: The diagnosis this test investigated (optional)
        #   result: A summary of what the test showed
        #   planned: True if this is a future/recommended test, False or omitted
        #           if it's a past test that already happened

        lab(
            "Complete Blood Count",
            date(2024, 3, 16),
            "Routine CBC performed day after birth",
            linked_encounter="Birth / NICU Admission",
            linked_diagnosis="Trisomy 21",
            result="Normal",
        ),

        lab(
            "Echocardiogram",
            date(2024, 4, 2),
            "Initial echo showing complete AVSD",
            linked_encounter="Cardiology Consult",
            linked_diagnosis="Complete AVSD",
            result="Complete AVSD with large primum ASD and VSD",
        ),

        lab(
            "Thyroid Function Test",
            date(2024, 9, 10),
            "TSH elevated, free T4 normal",
            linked_encounter="Genetics Follow-up",
            linked_diagnosis="Hypothyroidism",
            result="Hypothyroidism",
        ),


        # ── ENCOUNTERS ────────────────────────────────────────────────────
        # WHAT IS AN ENCOUNTER?
        # An encounter is a documented interaction between the patient and the
        # healthcare system. It's a visit, admission, or interaction where
        # clinical work happens. Examples include:
        # - Doctor office visits
        # - Hospital emergency room visits
        # - Hospital admissions and inpatient stays
        # - Surgical procedures
        # - Specialist consultations
        #
        # Encounters are the PRIMARY ANCHOR EVENTS on the timeline. This patient
        # has had five encounters so far (from 2024 to 2025). When a user clicks
        # on an encounter, the app shows all diagnoses and labs linked to that
        # encounter, painting a picture of "what happened during this visit?"
        #
        # Encounters are also where other events link back. A diagnosis or lab
        # that carries linked_encounter="Cardiology Consult" is saying: "This
        # diagnosis was made at, or this lab was ordered during, the Cardiology
        # Consult encounter."

        encounter(
            "Birth / NICU Admission",
            date(2024, 3, 15),
            "Born at 37 weeks, NICU stay for feeding support",
            location="Main Hospital NICU",
        ),

        encounter(
            "Cardiology Consult",
            date(2024, 4, 2),
            "Initial cardiology evaluation",
            provider="Dr. Martinez",
        ),

        encounter(
            "Cardiac Surgery",
            date(2024, 8, 20),
            "Complete AVSD repair — successful",
            provider="Dr. Chen",
            location="Main Hospital OR",
        ),

        encounter(
            "Genetics Follow-up",
            date(2024, 11, 5),
            "Routine genetics clinic visit; hypothyroidism identified on labs",
            provider="Dr. Patel",
        ),

        encounter(
            "Developmental Eval",
            date(2025, 2, 10),
            "6-month developmental milestone check",
            provider="Dr. Kim",
        ),


        # ── THERAPEUTICS ──────────────────────────────────────────────────
        # WHAT ARE THERAPEUTICS?
        # Therapeutics are interventions provided to the patient. There are
        # two main subtypes:
        #
        #   1. COUNSELING (psychosocial, educational, and therapy interventions):
        #      These are non-medication interventions that help the patient or
        #      family. Examples include:
        #      - Family education and support groups: teaching parents about the
        #        condition and connecting them with resources
        #      - Therapy referrals: physical therapy, occupational therapy,
        #        speech-language pathology
        #      - Pre-operative counseling: explaining surgery risks and recovery
        #      - Behavioral health screening or counseling
        #      - Nutrition counseling
        #      These events support linked_encounter (which visit initiated the
        #      counseling?) and optionally provider (who delivered it?).
        #
        #   2. MEDICATION (drug starts, dose adjustments, discontinuations):
        #      These are pharmaceutical interventions. Examples include:
        #      - Starting a medication to treat a problem
        #      - Adjusting a dose (e.g., increasing based on weight gain)
        #      - Discontinuing a medication (e.g., stopping a diuretic after
        #        surgery because it's no longer needed)
        #      These events support linked_encounter (which visit initiated the
        #      medication change?) and linked_diagnosis (what problem is this
        #      treating?), plus optional fields like dose and frequency.
        #
        # Both subtypes can optionally carry planned=True to indicate they are
        # recommended future actions (not yet done).

        # -- Counseling events --

        counseling(
            "Early Intervention Referral",
            date(2024, 3, 15),
            "Referred to early intervention program for developmental support",
            linked_encounter="Birth / NICU Admission",
            provider="Social Work",
        ),

        counseling(
            "Family Education — Down Syndrome",
            date(2024, 3, 15),
            "Parents provided with Down syndrome resources and support group info",
            linked_encounter="Birth / NICU Admission",
            provider="Genetics Team",
        ),

        counseling(
            "Cardiology Pre-op Counseling",
            date(2024, 4, 2),
            "Surgical risks, recovery timeline, and expectations discussed with family",
            linked_encounter="Cardiology Consult",
            provider="Dr. Martinez",
        ),

        counseling(
            "Developmental Therapy Referral",
            date(2025, 2, 10),
            "Referred to speech, occupational, and physical therapy",
            linked_encounter="Developmental Eval",
            provider="Dr. Kim",
        ),


        # -- Medication events --

        medication(
            "Furosemide",
            date(2024, 4, 2),
            "Started for fluid management in the setting of complete AVSD",
            linked_encounter="Cardiology Consult",
            linked_diagnosis="Complete AVSD",
            dose="2 mg",
            frequency="BID",
        ),

        medication(
            "Furosemide — Discontinued",
            date(2024, 9, 1),
            "Discontinued post-operatively once cardiac function normalised",
            linked_encounter="Cardiac Surgery",
            linked_diagnosis="Complete AVSD",
        ),

        medication(
            "Levothyroxine",
            date(2024, 11, 5),
            "Started for hypothyroidism after elevated TSH confirmed",
            linked_encounter="Genetics Follow-up",
            linked_diagnosis="Hypothyroidism",
            dose="25 mcg",
            frequency="Daily",
        ),


        # ==================================================================
        # PLANNED / FUTURE EVENTS  (AAP 2022 Health Supervision Guidelines)
        # ==================================================================
        #
        # WHAT ARE "PLANNED" EVENTS?
        # All events below are guideline-recommended screenings, visits, and
        # interventions for a child with Down syndrome that HAVE NOT YET HAPPENED.
        # They are future care recommendations based on clinical guidelines.
        # The key flag is planned=True, which tells the frontend:
        #   - Render these differently from past events (e.g., with a different
        #     color or style to show they're aspirational/future)
        #   - Show a "Sample Order" or "Schedule" button so a clinician can
        #     quickly create these in the real EHR when the time comes
        #
        # WHAT ARE THE AAP GUIDELINES?
        # The American Academy of Pediatrics (AAP) publishes evidence-based
        # clinical practice guidelines. For children with Down syndrome (Trisomy 21),
        # the AAP released comprehensive "Health Supervision for Children and
        # Adolescents With Down Syndrome" guidelines in:
        #
        #   Reference: American Academy of Pediatrics. Health Supervision for
        #              Children and Adolescents With Down Syndrome. Pediatrics.
        #              2022;149(5):e2022057010.
        #              (Available: https://pediatrics.aappublications.org)
        #
        # These guidelines recommend:
        # - Which screenings to do at each age (hearing, vision, thyroid, etc.)
        # - Which specialists to see and how often
        # - Which vaccinations and preventive measures are important
        # - What symptoms to watch for
        # - How to support development and education
        #
        # The guidelines exist because children with Down syndrome have elevated
        # risk for certain conditions (heart disease, hearing loss, thyroid disease,
        # leukemia, etc.), so early detection and proactive management improve
        # outcomes dramatically.
        #
        # DESIGN PATTERN:
        # Each planned event carries a guideline parameter (e.g.,
        # guideline="AAP 2022 §Thyroid — TSH annually") that cites which part
        # of the guidelines recommended it. This helps clinicians and patients
        # understand the evidence behind the recommendation.
        # ------------------------------------------------------------------


        # ── PLANNED ENCOUNTERS ────────────────────────────────────────────

        encounter(
            "DS Clinic — 2-Year Well-Child",
            date(2026, 6, 15),
            "Annual Down syndrome clinic visit. Review growth, development, "
            "nutrition, and update problem list per AAP guidelines.",
            provider="DS Clinic Team",
            planned=True,
            guideline="AAP 2022 §Health Supervision Visit — annually",
        ),

        encounter(
            "Audiology Annual Evaluation",
            date(2026, 8, 10),
            "Ear-specific audiologic evaluation. AAP recommends annually for "
            "all children with Down syndrome due to increased risk of hearing loss.",
            provider="Audiology",
            planned=True,
            guideline="AAP 2022 §Hearing — annual ear-specific audiologic evaluation",
        ),

        encounter(
            "Ophthalmology Evaluation",
            date(2026, 10, 5),
            "Ophthalmologic evaluation for refractive errors, strabismus, and "
            "nasolacrimal duct obstruction. Recommended every 1-2 years.",
            provider="Pediatric Ophthalmology",
            planned=True,
            guideline="AAP 2022 §Vision — evaluation every 1-2 years",
        ),

        encounter(
            "Cardiology Annual Follow-up",
            date(2026, 12, 1),
            "Post-surgical follow-up for repaired complete AVSD. Assess cardiac "
            "function and valve competence.",
            provider="Dr. Martinez",
            planned=True,
            guideline="AAP 2022 §Cardiac — ongoing follow-up post repair",
        ),

        encounter(
            "DS Clinic — 3-Year Well-Child",
            date(2027, 6, 15),
            "Annual Down syndrome clinic visit. Developmental milestones, "
            "early intervention → preschool transition planning.",
            provider="DS Clinic Team",
            planned=True,
            guideline="AAP 2022 §Health Supervision Visit — annually",
        ),

        encounter(
            "Sleep Study (Polysomnography)",
            date(2027, 9, 15),
            "Universal polysomnography recommended for all children with Down "
            "syndrome by age 3-4. Screens for obstructive sleep apnea, which "
            "affects ~50-80% of children with DS.",
            provider="Sleep Medicine",
            planned=True,
            guideline="AAP 2022 §Sleep — polysomnography by age 4",
        ),

        encounter(
            "Dental Evaluation",
            date(2027, 3, 15),
            "Routine dental evaluation. AAP recommends dental home established "
            "by age 1, visits every 6 months. Assess for delayed eruption, "
            "malocclusion, and periodontal disease.",
            provider="Pediatric Dentistry",
            planned=True,
            guideline="AAP 2022 §Dental — every 6 months",
        ),

        encounter(
            "DS Clinic — 4-Year Well-Child",
            date(2028, 6, 15),
            "Annual Down syndrome clinic visit. School readiness assessment, "
            "cervical spine clinical evaluation, and growth review.",
            provider="DS Clinic Team",
            planned=True,
            guideline="AAP 2022 §Health Supervision Visit — annually",
        ),


        # ── PLANNED LABS ──────────────────────────────────────────────────

        lab(
            "Thyroid Function Test (Annual)",
            date(2026, 6, 15),
            "Annual TSH screening per AAP guidelines. Risk of hypothyroidism "
            "increases with age in Down syndrome.",
            linked_encounter="DS Clinic — 2-Year Well-Child",
            linked_diagnosis="Hypothyroidism",
            planned=True,
            guideline="AAP 2022 §Thyroid — TSH annually",
        ),

        lab(
            "Complete Blood Count (Annual)",
            date(2026, 6, 15),
            "Annual CBC to monitor for hematologic abnormalities. Children with "
            "Down syndrome have 10-20x higher risk of leukemia, hence annual CBC "
            "to detect it early.",
            linked_encounter="DS Clinic — 2-Year Well-Child",
            linked_diagnosis="Trisomy 21",
            planned=True,
            guideline="AAP 2022 §Hematology — annual CBC",
        ),

        lab(
            "Celiac Disease Screen (tTG-IgA)",
            date(2026, 6, 15),
            "Initial celiac disease screening. AAP recommends screening around "
            "age 2 in children with Down syndrome on a gluten-containing diet, "
            "or earlier if symptomatic.",
            linked_encounter="DS Clinic — 2-Year Well-Child",
            linked_diagnosis="Trisomy 21",
            planned=True,
            guideline="AAP 2022 §GI — celiac screen by age 2",
        ),

        lab(
            "Thyroid Function Test (Annual)",
            date(2027, 6, 15),
            "Annual TSH screening. Continue to monitor thyroid function while "
            "on levothyroxine replacement therapy.",
            linked_encounter="DS Clinic — 3-Year Well-Child",
            linked_diagnosis="Hypothyroidism",
            planned=True,
            guideline="AAP 2022 §Thyroid — TSH annually",
        ),

        lab(
            "Complete Blood Count (Annual)",
            date(2028, 6, 15),
            "Annual CBC to monitor for hematologic abnormalities.",
            linked_encounter="DS Clinic — 4-Year Well-Child",
            linked_diagnosis="Trisomy 21",
            planned=True,
            guideline="AAP 2022 §Hematology — annual CBC",
        ),

        lab(
            "Thyroid Function Test (Annual)",
            date(2028, 6, 15),
            "Annual TSH screening.",
            linked_encounter="DS Clinic — 4-Year Well-Child",
            linked_diagnosis="Hypothyroidism",
            planned=True,
            guideline="AAP 2022 §Thyroid — TSH annually",
        ),

        lab(
            "Cervical Spine Clinical Assessment",
            date(2028, 6, 15),
            "Clinical assessment of cervical spine stability. AAP recommends "
            "screening for atlantoaxial instability symptoms at each visit "
            "beginning at age 3-5. Imaging if symptomatic.",
            linked_encounter="DS Clinic — 4-Year Well-Child",
            linked_diagnosis="Trisomy 21",
            planned=True,
            guideline="AAP 2022 §Musculoskeletal — cervical spine assessment",
        ),


        # ── PLANNED THERAPEUTICS — COUNSELING ─────────────────────────────

        counseling(
            "Nutrition Assessment",
            date(2026, 6, 15),
            "Nutritional evaluation and dietary counseling. Children with Down "
            "syndrome are at increased risk for obesity; monitor BMI and provide "
            "anticipatory guidance on healthy eating.",
            linked_encounter="DS Clinic — 2-Year Well-Child",
            provider="Dietitian",
            planned=True,
            guideline="AAP 2022 §Nutrition — assess at each visit",
        ),

        counseling(
            "Speech-Language Therapy Review",
            date(2026, 8, 1),
            "Ongoing speech-language therapy progress review. Children with DS "
            "typically have expressive language delays; adjust therapy goals.",
            linked_encounter="DS Clinic — 2-Year Well-Child",
            provider="Speech-Language Pathology",
            planned=True,
            guideline="AAP 2022 §Development — ongoing speech therapy",
        ),

        counseling(
            "EI → Preschool Transition Planning",
            date(2027, 2, 15),
            "Plan transition from Early Intervention (Part C) to preschool "
            "special education services (Part B) at age 3. IEP development.",
            linked_encounter="DS Clinic — 3-Year Well-Child",
            provider="DS Clinic Team",
            planned=True,
            guideline="AAP 2022 §Development — transition planning at age 3",
        ),

        counseling(
            "Behavioral Assessment",
            date(2027, 6, 15),
            "Screen for behavioral concerns including ADHD, anxiety, and autism "
            "spectrum disorder, which co-occur at higher rates in Down syndrome.",
            linked_encounter="DS Clinic — 3-Year Well-Child",
            provider="Developmental Pediatrics",
            planned=True,
            guideline="AAP 2022 §Behavior — screen at each visit",
        ),

        counseling(
            "School Readiness Assessment",
            date(2028, 6, 15),
            "Comprehensive developmental and educational assessment for school "
            "readiness. Review IEP goals and transition to kindergarten planning.",
            linked_encounter="DS Clinic — 4-Year Well-Child",
            provider="Developmental Pediatrics",
            planned=True,
            guideline="AAP 2022 §Development — school readiness by age 5",
        ),


        # ── PLANNED THERAPEUTICS — MEDICATION ─────────────────────────────

        medication(
            "Levothyroxine — Dose Review",
            date(2026, 6, 15),
            "Review levothyroxine dose based on TSH results and weight gain. "
            "Adjust dose as needed for growth.",
            linked_encounter="DS Clinic — 2-Year Well-Child",
            linked_diagnosis="Hypothyroidism",
            planned=True,
            guideline="AAP 2022 §Thyroid — monitor therapy",
        ),

        medication(
            "Levothyroxine — Dose Review",
            date(2027, 6, 15),
            "Annual levothyroxine dose review based on updated TSH and growth.",
            linked_encounter="DS Clinic — 3-Year Well-Child",
            linked_diagnosis="Hypothyroidism",
            planned=True,
            guideline="AAP 2022 §Thyroid — monitor therapy",
        ),

    ]


# ---------------------------------------------------------------------------
# load_problem_list
# ---------------------------------------------------------------------------

def load_problem_list():
    """
    Build the problem list automatically from the diagnosis events above.

    DESIGN PATTERN — DERIVING DATA INSTEAD OF DUPLICATING:
    This function demonstrates an important software design principle: avoid
    duplicating data. Instead of maintaining a separate list of problems with
    redundant name, status, date, and ICD-10 code, we derive the problem list
    automatically from the diagnosis events above.

    When you edit a diagnosis (change its status, update its ICD-10 code, etc.),
    the problem list automatically reflects that change. No need to update two
    places. This is called the "Single Source of Truth" principle.

    HOW IT WORKS — STEP BY STEP:
    The function returns a list of Problem objects built using a list
    comprehension. Here's what happens in detail:

    1. for ev in load_sample_events()
       This loop iterates through EVERY event returned by load_sample_events().
       Each event (ev) is a ClinicalEvent object with fields like label,
       event_date, category, description, and details.

    2. if ev.category == Category.DIAGNOSIS
       This filter keeps ONLY the diagnosis events. We check if the event's
       category field equals Category.DIAGNOSIS. All non-diagnosis events
       (labs, encounters, medications, counseling) are skipped. This is why
       we have a filter: we only want to create Problem objects from diagnoses,
       not from other event types.

    3. problem(name=ev.label, onset_date=ev.event_date, ...)
       For each diagnosis event that passed the filter, we construct a Problem
       object. We pull the values from the diagnosis event:
       - The diagnosis label becomes the problem name
       - The diagnosis date becomes the problem onset date
       - The status field from the diagnosis becomes the problem status
       - The icd10 code stays as-is
       - The description explains what the problem is
       All these values come from the diagnosis() call made above.

    RESULT:
    The function returns a list of Problem objects, one for each diagnosis.
    The problem list shown in the UI comes from this function. If you add a
    new diagnosis in load_sample_events(), it will automatically appear in
    the problem list. If you change a diagnosis's status from 'active' to
    'resolved', the problem list will reflect that change immediately.
    """
    return [
        problem(
            name=ev.label,
            onset_date=ev.event_date,
            # status defaults to 'active' if not set in the diagnosis() call
            status=ev.details.get("status", "active"),
            icd10=ev.details.get("icd10", ""),
            description=ev.description,
        )
        for ev in load_sample_events()
        if ev.category == Category.DIAGNOSIS
    ]
