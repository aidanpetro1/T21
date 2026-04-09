# T21 Clinical Timeline

An interactive clinical timeline application for tracking the care of a patient with Trisomy 21 (Down syndrome). Built with Python and Plotly.js.

## Features

- **Interactive timeline** — Zoom, pan, and click events to see full details
- **Category filters** — Toggle Encounters, Diagnoses, Labs, and Therapeutics on/off
- **Problem list panel** — Collapsible side panel showing active and resolved diagnoses with linked labs
- **Event cross-referencing** — Click an encounter to see all diagnoses, labs, and therapeutics from that visit
- **AAP-guided planned events** — Future screenings and visits based on the [AAP 2022 Health Supervision Guidelines](https://publications.aap.org/pediatrics/article/149/5/e2022057010/186778) are shown as hollow pastel markers
- **Sample Order button** — Planned events include a "Sample Order" button with pre-filled clinical order details
- **Today indicator** — A red dashed vertical line marks the current date

## Getting Started

```bash
cd app
python app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

**Requirements:** Python 3.7+ (no external packages needed — uses only the standard library).

## Project Structure

```
T21_project/
├── app/
│   ├── app.py            # Web server entry point
│   ├── models.py         # Data structures (ClinicalEvent, Problem)
│   ├── sample_data.py    # Sample patient data + AAP planned events
│   └── templates/
│       └── timeline.html # Frontend (HTML + CSS + Plotly.js)
├── .gitignore
└── README.md
```

## Architecture

The app follows a simple server-side rendering pattern:

1. `models.py` defines the data structures (`ClinicalEvent`, `Problem`) and their visual properties (colors, marker symbols)
2. `sample_data.py` provides hardcoded clinical events for one patient, including AAP-guideline planned future events
3. `app.py` runs a Python HTTP server that reads the HTML template, injects the clinical data as JSON, and serves the page
4. `timeline.html` uses Plotly.js to render the interactive chart, with JavaScript handling filtering, popups, and the sample order panel

## Learning

Every file is heavily commented to explain Python concepts, web development patterns, and clinical terminology. The codebase is designed to be readable by novice programmers.
