"""
models.py
---------
Defines the core data structures for the clinical timeline.

There are two main concepts here:

  1. ClinicalEvent  — a single point in time shown on the timeline.
                      Can be a Diagnosis, Encounter, Lab, or Therapeutic.

  2. Problem        — a summary entry in the problem list, derived
                      from Diagnosis events.

Relationships between events
-----------------------------
  Encounters are the primary entity on the timeline.
  Diagnoses, Labs, and Therapeutics can all be linked to an encounter
  (linked_encounter) so that clicking an encounter shows what was
  addressed, ordered, and initiated during that visit.
  Labs can also be linked to a specific diagnosis (linked_diagnosis)
  to preserve the clinical cross-reference in the problem list.

  Encounter  <──  Diagnosis    (linked_encounter = encounter label)
  Encounter  <──  Lab          (linked_encounter = encounter label)
  Encounter  <──  Therapeutic  (linked_encounter = encounter label)
  Diagnosis  <──  Lab          (linked_diagnosis = diagnosis label)

Therapeutic subtypes
--------------------
  The THERAPEUTIC category has two subtypes, set via the `subtype` field
  in details{}. Each subtype gets its own colour and marker shape so they
  are visually distinct on the same timeline row.

    subtype="counseling"  — diamond marker, orange
    subtype="medication"  — hexagon marker, purple

  Use the counseling() and medication() convenience constructors rather
  than calling ClinicalEvent directly.

Key Python Concepts Used in This File
--------------------------------------
  1. Enums (Enumeration)
     — An Enum is a class where each instance represents one of a fixed set
       of allowed values. Used here for Category and ProblemStatus to avoid typos.
       When you inherit from BOTH str and Enum (e.g., class Category(str, Enum)),
       each enum member is also a string, so it can be used directly in JSON.

  2. Dataclasses (@dataclass decorator)
     — A dataclass automatically generates __init__, __repr__, and other methods
       for you based on the field definitions. It reduces boilerplate code.
     — Example: @dataclass with category, label, event_date fields automatically
       creates an __init__(self, category, label, event_date, ...) for you.

  3. Properties (@property decorator)
     — A @property turns a method into a read-only attribute. Instead of calling
       obj.is_planned(), you just read obj.is_planned as if it were a field.
     — The method runs behind the scenes each time you access the property.

  4. **kwargs (keyword arguments unpacking)
     — **kwargs collects any extra keyword arguments into a dictionary.
     — Example: def diagnosis(..., **details) means diagnosis(icd10="Q90.0")
       puts {"icd10": "Q90.0"} into the details dict.

  5. Type hints (: Type syntax)
     — Annotations like category: Category and event_date: date tell you what
       type each variable should hold. Python doesn't enforce them, but they
       help with documentation and IDE support.

  6. dict.get(key, default)
     — A safe way to read a dict value. If the key doesn't exist, it returns
       the default instead of crashing. Example: self.details.get("planned", False)
       means "get the 'planned' key, or return False if it's not there".
"""

# from __future__ import annotations
# This import (available in Python 3.7+) lets you use class names as type hints
# before the class is fully defined. Without it, you'd get a NameError if you
# tried to use a class name in its own type hints. With it, all type hints are
# treated as strings internally and evaluated lazily, which is safer.
from __future__ import annotations

# from dataclasses import dataclass, field
# dataclass: A decorator that auto-generates __init__, __repr__, __eq__ and other
#            dunder methods based on field definitions, reducing boilerplate.
# field: A function used to customize dataclass field behaviour, e.g., default_factory
#        for mutable defaults (see ClinicalEvent.details below).
from dataclasses import dataclass, field

# from datetime import date
# date: A class representing calendar dates (YYYY-MM-DD) without time-of-day.
#       Used here because clinical events are recorded at the day level.
from datetime import date

# from enum import Enum
# Enum: A base class for creating enumerations — fixed sets of allowed values.
#       Much safer than using plain strings, since typos are caught at import time.
from enum import Enum

# from typing import Optional
# Optional[X]: A type hint meaning "either X or None" (no value).
#              Useful for documenting which fields can be missing.
from typing import Optional


# ---------------------------------------------------------------------------
# Category Enum
# ---------------------------------------------------------------------------
# An Enum is used instead of plain strings so that typos are caught at
# import time rather than silently producing wrong behaviour at runtime.
#
# Here, Category inherits from BOTH str and Enum. This means:
#   - Each Category member IS a string (e.g., Category.DIAGNOSIS == "diagnosis")
#   - You can use Category.DIAGNOSIS directly in JSON (no .value needed in many contexts)
#   - You get all the enum safety benefits plus string compatibility

class Category(str, Enum):
    DIAGNOSIS    = "diagnosis"
    ENCOUNTER    = "encounter"
    LAB          = "lab"
    THERAPEUTIC  = "therapeutic"   # parent type; subtypes are counseling / medication


# ---------------------------------------------------------------------------
# Visual Appearance — Hex Colours and Plotly Marker Symbols
# ---------------------------------------------------------------------------
# These dicts map Category/subtype values to visual properties consumed by Plotly.
#
# Hex colours: #RRGGBB format (e.g., #e74c3c is red). Each digit pair is 0-255 in hex.
# Plotly symbols: Shape names like "circle", "square", "diamond", etc.
#                 The "-open" suffix creates a hollow/outline-only variant.
#
# We use dicts (not separate variables) because:
#   1. It's easy to look up the right colour/symbol by category: CATEGORY_COLORS[cat]
#   2. It keeps visual mappings organized in one place (not scattered code)
#   3. It's simple to pass these to Plotly in the frontend
#
# These are referenced by ClinicalEvent.color / .symbol and are consumed
# directly by Plotly in the frontend.
# ---------------------------------------------------------------------------

CATEGORY_COLORS = {
    Category.DIAGNOSIS:   "#e74c3c",   # red
    Category.ENCOUNTER:   "#3498db",   # blue
    Category.LAB:         "#2ecc71",   # green
    Category.THERAPEUTIC: "#f1c40f",   # yellow — fallback if no subtype is set
}

CATEGORY_SYMBOLS = {
    Category.DIAGNOSIS:   "circle",
    Category.ENCOUNTER:   "square",
    Category.LAB:         "triangle-up",
    Category.THERAPEUTIC: "diamond",   # fallback if no subtype is set
}

# ---------------------------------------------------------------------------
# Planned (future) Event Colours
# ---------------------------------------------------------------------------
# AAP-guided future events use lighter, pastel variants of the base colours
# so they are visually distinct from historical/completed events.
# Marker symbols use the "-open" (hollow) variant automatically (see symbol property).
#
# A Hex colour code like #ff7675 is lighter/more saturated than #e74c3c because:
#   - The first two digits (RR) control red: ff > e7
#   - The middle two digits (GG) control green: 76 > 4c
#   - The last two digits (BB) control blue: 75 > 3c
#   So each channel is higher, creating a lighter appearance.

PLANNED_COLORS = {
    Category.DIAGNOSIS:   "#ff7675",   # pastel red
    Category.ENCOUNTER:   "#74b9ff",   # pastel blue
    Category.LAB:         "#55efc4",   # pastel green
    Category.THERAPEUTIC: "#ffeaa7",   # pastel yellow — fallback
}

PLANNED_SUBTYPE_COLORS = {
    "counseling": "#fab1a0",   # pastel orange
    "medication": "#a29bfe",   # pastel purple
}

# ---------------------------------------------------------------------------
# Therapeutic Subtypes — Colour and Symbol Overrides
# ---------------------------------------------------------------------------
# Because counseling and medication share the THERAPEUTIC category row on
# the timeline but need to look different, each subtype gets its own colour
# and Plotly marker symbol. These override the base CATEGORY_* values when
# the event's details["subtype"] is set.
#
# Why dicts instead of if/elif logic?
#   - Easy to look up: SUBTYPE_COLORS["counseling"] is cleaner than
#     if subtype == "counseling": return "#e67e22"
#   - Easy to extend: just add a new row to the dict
#   - Easy to test: can iterate over all subtypes and check properties
# ---------------------------------------------------------------------------

SUBTYPE_COLORS = {
    "counseling": "#e67e22",   # orange
    "medication":  "#9b59b6",  # purple
}

SUBTYPE_SYMBOLS = {
    "counseling": "diamond",
    "medication":  "hexagon",
}


# ---------------------------------------------------------------------------
# ClinicalEvent — The Core Data Structure
# ---------------------------------------------------------------------------
# The single shared dataclass for all event types. Using one class keeps
# the serialisation and frontend rendering logic simple — every event has
# the same JSON shape. Category-specific fields live in the `details` dict.
#
# What @dataclass does:
#   - Reads the field definitions (category: Category, label: str, etc.)
#   - Auto-generates __init__, __repr__, __eq__ and other methods
#   - Saves you from writing boilerplate code
#
# Why field(default_factory=dict) for details?
#   - Mutable Default Gotcha: if you wrote details: dict = {}, Python would
#     create ONE empty dict shared by ALL instances. Modifying it in one
#     instance would affect all others (a common bug).
#   - Solution: default_factory=dict tells Python "create a fresh empty dict
#     for each new instance". It calls dict() once per instance.

@dataclass
class ClinicalEvent:
    """A single event shown as a marker on the timeline."""

    # Core fields (required when creating a ClinicalEvent):
    category:   Category          # diagnosis | encounter | lab | therapeutic
    label:      str               # short display name, e.g. "Cardiac Surgery"
    event_date: date              # the date the event occurred (YYYY-MM-DD)

    # Optional fields (can be omitted, have defaults):
    description: str = ""        # free-text clinical note; defaults to empty string
    details: dict = field(default_factory=dict)
    # details is a catch-all dict holding any extra key-value pairs passed as **kwargs.
    # Examples: icd10 (ICD-10 diagnosis code), status ("active"/"resolved"),
    #           provider (doctor name), location (department), result (lab result),
    #           linked_encounter (which encounter this event belongs to),
    #           linked_diagnosis (which diagnosis a lab is related to),
    #           subtype ("counseling" or "medication" for THERAPEUTIC events),
    #           planned (True/False, marks AAP future events)

    # -- Convenience Properties (used by the frontend) --------------------
    # These @property methods act like read-only attributes. You access them
    # as obj.is_planned (no parentheses), but behind the scenes they call a method.

    @property
    def is_planned(self) -> bool:
        """
        True when this event is a future / AAP-guideline planned event.

        How it works:
          - dict.get("planned", False) safely reads the "planned" key from details.
            If the key doesn't exist, it returns False (the default).
          - bool() is called on the result to ensure we return a True/False value
            (in case someone stored a truthy value like 1 or "yes").
        """
        return bool(self.details.get("planned", False))

    @property
    def color(self) -> str:
        """
        Hex colour for this event's marker.
        Planned (future) events use lighter pastel colours.
        For THERAPEUTIC events, the subtype colour overrides the base
        category colour so counseling and medication are visually distinct.

        Logic step by step:
          1. If this is a THERAPEUTIC event (counseling or medication):
             a. Look up the subtype from details["subtype"] (empty string if missing)
             b. Check if it's a planned event: if so, use PLANNED_SUBTYPE_COLORS,
                else use SUBTYPE_COLORS
             c. Look up the colour for this subtype using dict.get(subtype, fallback)
                If the subtype isn't found, use the fallback (base category colour)
          2. Else (for other categories like DIAGNOSIS, ENCOUNTER, LAB):
             a. Pick PLANNED_COLORS or CATEGORY_COLORS based on is_planned
             b. Look up the colour for this category
        """
        if self.category == Category.THERAPEUTIC:
            # This is a counseling or medication event; check for subtype-specific colour
            subtype = self.details.get("subtype", "")
            # Choose colour palette: pastel if planned, vivid if active/historical
            sub_colors = PLANNED_SUBTYPE_COLORS if self.is_planned else SUBTYPE_COLORS
            # Fallback palette if subtype isn't recognized
            fallback   = PLANNED_COLORS if self.is_planned else CATEGORY_COLORS
            # Try to get the subtype colour; if not found, use the fallback
            return sub_colors.get(subtype, fallback[self.category])
        # For non-therapeutic events, just pick the colour based on category
        colors = PLANNED_COLORS if self.is_planned else CATEGORY_COLORS
        return colors[self.category]

    @property
    def symbol(self) -> str:
        """
        Plotly marker symbol for this event.
        Planned events use hollow/open marker variants.
        Same subtype-override logic as color above.

        The "-open" suffix trick:
          - "circle" is a solid filled circle
          - "circle-open" is the same circle but hollow/outline-only
          - We concatenate "-open" to base symbols for planned events:
            base + "-open" where base might be "circle", "diamond", etc.
        """
        if self.category == Category.THERAPEUTIC:
            # Look up the symbol for this therapeutic subtype
            subtype = self.details.get("subtype", "")
            base = SUBTYPE_SYMBOLS.get(subtype, CATEGORY_SYMBOLS[self.category])
        else:
            # For non-therapeutic events, use the category's default symbol
            base = CATEGORY_SYMBOLS[self.category]
        # Add "-open" suffix if this is a planned (future) event, otherwise use base
        return base + "-open" if self.is_planned else base

    def to_dict(self) -> dict:
        """
        Serialise this ClinicalEvent to a plain Python dict so it can be
        JSON-encoded and injected into the HTML template. The frontend reads
        these fields directly.

        Why do we need this?
          - Dataclass instances (ClinicalEvent objects) cannot be converted to JSON
            directly. Only simple types (dict, list, str, int, date, etc.) can.
          - This method transforms the dataclass into a dict with JSON-safe types.

        Special conversions:
          - self.category.value: the Category enum's string value (e.g., "diagnosis")
          - self.event_date.isoformat(): converts date to "YYYY-MM-DD" string
            (e.g., date(2023, 5, 15) becomes "2023-05-15")
          - All other fields are already JSON-safe (str, bool, dict)
        """
        return {
            "category":   self.category.value,  # enum → string
            "label":      self.label,
            "event_date": self.event_date.isoformat(),  # date → "YYYY-MM-DD"
            "description": self.description,
            "color":      self.color,
            "symbol":     self.symbol,
            "details":    self.details,
            "planned":    self.is_planned,
        }


# ---------------------------------------------------------------------------
# Convenience Constructors
# ---------------------------------------------------------------------------
# These functions are thin wrappers around ClinicalEvent that make the
# sample_data.py (and future data loaders) read naturally.
#
# Why use these instead of calling ClinicalEvent() directly?
#   - The function names (diagnosis(), medication()) are more readable
#   - They handle category assignment automatically (one less argument to pass)
#   - They organize related parameters (e.g., linked_encounter, status)
#   - They simplify using **kwargs to build up the details dict
#
# How **kwargs works:
#   - def diagnosis(..., **details): means "accept any keyword arguments"
#   - diagnosis(icd10="Q90.0", other_field="value") → details = {"icd10": ..., ...}
#   - The function can then add more keys: details["status"] = status
#   - Finally, it creates ClinicalEvent(..., details=details)

def diagnosis(label: str, event_date: date, description: str = "",
              status: str = "active",
              linked_encounter: str = "",
              **details) -> ClinicalEvent:
    """
    Create a Diagnosis event.

    Parameters
    ----------
    label : str
        Short display name, e.g. "Trisomy 21"
    event_date : date
        The date this diagnosis was made (YYYY-MM-DD)
    description : str, optional
        Free-text clinical note (default: empty string)
    status : str, optional
        "active" or "resolved" — shown in the problem list (default: "active")
    linked_encounter : str, optional
        Label of the Encounter where this was diagnosed.
        Used to cross-reference from an encounter's popup (default: empty)
    **details : keyword arguments
        Any extra fields, e.g. icd10='Q90.0', provider='Dr. Smith'
        These are stored in the event's details dict and appear in the popup.

    How it works (building up details):
      1. Start with any **kwargs passed (e.g., icd10='Q90.0')
      2. Add status and linked_encounter to the dict
      3. Pass the completed dict to ClinicalEvent()
    """
    # Start with whatever extra kwargs the caller passed
    details["status"] = status
    if linked_encounter:
        details["linked_encounter"] = linked_encounter
    # Create and return the ClinicalEvent with all accumulated details
    return ClinicalEvent(Category.DIAGNOSIS, label, event_date, description, details=details)


def encounter(label: str, event_date: date, description: str = "",
              **details) -> ClinicalEvent:
    """
    Create an Encounter event.

    Parameters
    ----------
    label : str
        Short display name, e.g. "Cardiology Clinic" or "Surgery"
    event_date : date
        The date of the encounter (YYYY-MM-DD)
    description : str, optional
        Free-text clinical note (default: empty string)
    **details : keyword arguments
        Any extra fields, e.g. provider='Dr. Smith', location='OR',
        provider_type='Cardiologist', etc.
    """
    return ClinicalEvent(Category.ENCOUNTER, label, event_date, description, details=details)


def lab(label: str, event_date: date, description: str = "",
        linked_encounter: str = "",
        linked_diagnosis: str = "",
        **details) -> ClinicalEvent:
    """
    Create a Lab / investigation event.

    Parameters
    ----------
    label : str
        Lab name, e.g. "Genetic Panel" or "Echocardiogram"
    event_date : date
        The date the lab was performed (YYYY-MM-DD)
    description : str, optional
        Free-text clinical note (default: empty string)
    linked_encounter : str, optional
        Label of the Encounter where this lab was ordered.
        Used for cross-reference in the popup (default: empty)
    linked_diagnosis : str, optional
        Label of the Diagnosis this lab relates to.
        Used for cross-reference in the problem list (default: empty)
    **details : keyword arguments
        Any extra fields, e.g. result='Normal', method='NGS', units='mg/dL'
    """
    if linked_encounter:
        details["linked_encounter"] = linked_encounter
    if linked_diagnosis:
        details["linked_diagnosis"] = linked_diagnosis
    return ClinicalEvent(Category.LAB, label, event_date, description, details=details)


def counseling(label: str, event_date: date, description: str = "",
               linked_encounter: str = "",
               **details) -> ClinicalEvent:
    """
    Create a Counseling therapeutic event (subtype of THERAPEUTIC).

    Counseling covers psychosocial support, therapy referrals, family
    education, and similar non-pharmacological interventions.

    Parameters
    ----------
    label : str
        Short name, e.g. "Early Intervention Referral" or "Psychology Consult"
    event_date : date
        The date counseling was initiated or discussed (YYYY-MM-DD)
    description : str, optional
        Free-text clinical note (default: empty string)
    linked_encounter : str, optional
        Label of the Encounter where this was discussed (default: empty)
    **details : keyword arguments
        Any extra fields, e.g. provider='Dr. Smith', duration='6 weeks'

    How it works:
      - Sets details["subtype"] = "counseling" so the frontend renders it
        with the counseling colour (orange) and symbol (diamond)
      - All other logic is the same as diagnosis() or medication()
    """
    # Mark the subtype so the frontend can assign the correct colour/symbol
    details["subtype"] = "counseling"
    if linked_encounter:
        details["linked_encounter"] = linked_encounter
    return ClinicalEvent(Category.THERAPEUTIC, label, event_date, description, details=details)


def medication(label: str, event_date: date, description: str = "",
               linked_encounter: str = "",
               linked_diagnosis: str = "",
               **details) -> ClinicalEvent:
    """
    Create a Medication therapeutic event (subtype of THERAPEUTIC).

    Covers medication starts, dose changes, and discontinuations.

    Parameters
    ----------
    label : str
        Drug name, e.g. "Levothyroxine" or "Aspirin"
    event_date : date
        The date the medication was started/changed/stopped (YYYY-MM-DD)
    description : str, optional
        Free-text clinical note (default: empty string)
    linked_encounter : str, optional
        Label of the Encounter where this was prescribed (default: empty)
    linked_diagnosis : str, optional
        Label of the Diagnosis this medication is treating (default: empty)
    **details : keyword arguments
        Any extra fields, e.g. dose='25 mcg', frequency='Daily',
        route='Oral', manufacturer='Synthroid'

    How it works:
      - Sets details["subtype"] = "medication" so the frontend renders it
        with the medication colour (purple) and symbol (hexagon)
      - This is visually distinct from counseling events on the same row
    """
    details["subtype"] = "medication"
    if linked_encounter:
        details["linked_encounter"] = linked_encounter
    if linked_diagnosis:
        details["linked_diagnosis"] = linked_diagnosis
    return ClinicalEvent(Category.THERAPEUTIC, label, event_date, description, details=details)


# ---------------------------------------------------------------------------
# Problem & ProblemStatus — The Problem List
# ---------------------------------------------------------------------------
# The problem list is a curated index of diagnoses that summarizes the
# patient's clinical state. It is derived automatically from diagnosis events
# in sample_data.load_problem_list(), so there is no need to maintain it
# separately.
#
# Design rationale:
#   - Problem is its own dataclass (not just a ClinicalEvent) because the
#     problem list has a different UI and fewer fields (no colour/symbol).
#   - ProblemStatus(str, Enum) restricts status to "active" or "resolved"
#     (safer than allowing any string, which could lead to typos).
# ---------------------------------------------------------------------------

class ProblemStatus(str, Enum):
    """
    Enumeration of valid problem statuses.

    Why inherit from both str and Enum?
      - str: allows ProblemStatus.ACTIVE to be used directly as a string
      - Enum: restricts the allowed values to ACTIVE or RESOLVED only
      - Result: ProblemStatus.ACTIVE == "active" and you can use it in JSON
    """
    ACTIVE   = "active"
    RESOLVED = "resolved"


@dataclass
class Problem:
    """
    A single entry in the patient's problem list.

    Fields:
    ------
    name : str
        The problem/diagnosis name, e.g. "Trisomy 21"
    onset_date : date
        The date the problem was first diagnosed (YYYY-MM-DD)
    status : ProblemStatus, optional
        Either ACTIVE or RESOLVED (default: ACTIVE).
        Restricts status to these two values for safety.
    icd10 : str, optional
        ICD-10 diagnosis code, e.g. "Q90.0" (default: empty)
    description : str, optional
        Free-text clinical details (default: empty)

    Why separate from ClinicalEvent?
      - Problem list has a different UI (table, not timeline)
      - Fewer fields (no colour/symbol, no arbitrary details dict)
      - Derives from diagnosis events, but isn't itself a timeline event
    """

    name:        str
    onset_date:  date
    status:      ProblemStatus = ProblemStatus.ACTIVE
    icd10:       str = ""
    description: str = ""

    def to_dict(self) -> dict:
        """
        Serialise for JSON transport to the frontend.

        Conversions:
          - self.status.value: the enum's string value, e.g. "active"
          - self.onset_date.isoformat(): date to "YYYY-MM-DD" string
        """
        return {
            "name":        self.name,
            "onset_date":  self.onset_date.isoformat(),
            "status":      self.status.value,
            "icd10":       self.icd10,
            "description": self.description,
        }


def problem(name: str, onset_date: date, status: str = "active",
            icd10: str = "", description: str = "") -> Problem:
    """
    Convenience constructor for creating a Problem entry.
    Mirrors the diagnosis() pattern for consistency.

    Parameters
    ----------
    name : str
        Problem name, e.g. "Trisomy 21"
    onset_date : date
        The date the problem was diagnosed (YYYY-MM-DD)
    status : str, optional
        Either "active" or "resolved" (default: "active")
    icd10 : str, optional
        ICD-10 code, e.g. "Q90.0" (default: empty)
    description : str, optional
        Free-text notes (default: empty)

    Returns
    -------
    Problem
        A new Problem instance with the given fields.

    How it works:
      - Takes a string status ("active" or "resolved")
      - Converts it to a ProblemStatus enum using ProblemStatus(status)
      - This ensures only valid status values are accepted; ProblemStatus("invalid")
        would raise an error, catching typos early
      - Passes the enum to the Problem dataclass
    """
    return Problem(name, onset_date, ProblemStatus(status), icd10, description)
