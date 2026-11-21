# AquaSentinel AI

### An AI-Powered Predictive Urban Water Intelligence and Equitable Resource Allocation System

**AquaSentinel AI** is a prototype decision-support platform for
understanding water-consumption patterns, identifying unusual usage,
exploring equitable allocation under supply constraints, and simulating
shortage-and-recovery scenarios.

-   **Live application:** https://aquasentinel-ai-nxtwave.streamlit.app/
-   **GitHub repository:**
    https://github.com/Suhas2811/AquaSentinel_AI-Nxtwave_Hackathon
-   **Hackathon track:** Smart Grid & Urban Resource Allocation
    Controller

> **Prototype scope:** AquaSentinel AI is a research and demonstration
> prototype. It does not connect to, control, or issue commands to live
> municipal water infrastructure. Infrastructure and shortage scenarios
> are simulations.

------------------------------------------------------------------------

## Table of contents

-   [Problem](#problem)
-   [Solution](#solution)
-   [Core capabilities](#core-capabilities)
-   [Workflow](#workflow)
-   [Data](#data)
-   [Technology stack](#technology-stack)
-   [Repository structure](#repository-structure)
-   [Run locally](#run-locally)
-   [Gemini API configuration](#gemini-api-configuration)
-   [Forecasting validation](#forecasting-validation)
-   [Limitations and responsible use](#limitations-and-responsible-use)
-   [Future improvements](#future-improvements)

## Problem

Urban water systems must make decisions amid changing demand, unusual
consumption patterns, incomplete information, and constrained supply.
During shortages, allocation decisions should also account for essential
needs and the effects on different user groups.

AquaSentinel AI brings several decision-support capabilities into one
prototype so users can explore demand patterns, investigate anomalies,
compare allocation outcomes, and test shortage scenarios.

## Solution

The platform follows a four-stage workflow:

**Predict → Detect → Optimize → Explain**

1.  **Predict** expected water demand from historical consumption
    patterns.
2.  **Detect** unusual consumption behaviour that may warrant
    investigation.
3.  **Optimize** allocation under constrained supply while prioritizing
    essential needs.
4.  **Explain** scenario outcomes through an interactive crisis
    simulator and an AI-assisted project interface.

## Core capabilities

### 1. Overview

A central entry point to the platform and its urban water intelligence
workflow.

### 2. Demand forecasting

Uses historical consumption data and trained forecasting models to
estimate future demand. The page presents forecast outputs and model
evaluation information.

### 3. Anomaly detection

Analyses consumption patterns to flag unusual observations for further
investigation. An anomaly is an indicator for review, not proof of a
leak, fault, or misuse.

### 4. Resource optimization

Explores water allocation when available supply is constrained. The
allocation approach prioritizes essential needs and supports comparison
of allocation outcomes.

### 5. Crisis simulator

Allows users to explore synthetic water-shortage and recovery scenarios
by changing assumptions such as available supply, recovery rate, and
simulation horizon. It presents allocation, unmet demand,
essential-needs coverage, and scenario trends.

### 6. AI Agent

Provides a conversational interface for questions about AquaSentinel AI
and its modules. It uses the Gemini API when available and includes a
local fallback response path. The agent is informational; it does not
operate infrastructure.

## Workflow

  -----------------------------------------------------------------------
  Stage                   Purpose                 Output
  ----------------------- ----------------------- -----------------------
  Predict                 Estimate demand from    Forecasts and
                          historical consumption  evaluation metrics

  Detect                  Identify unusual        Records or sensors
                          consumption patterns    flagged for review

  Optimize                Allocate constrained    Allocation and shortage
                          supply with             indicators
                          essential-needs         
                          priority                

  Explain                 Explore assumptions and Scenario views and
                          ask questions about the assistant responses
                          platform                
  -----------------------------------------------------------------------

The stages are complementary. Forecasts can inform planning, anomaly
flags can guide investigation, optimization can explore allocation
choices, and simulation can help users understand the consequences of
different assumptions.

## Data

The project uses the **HSB Living Lab Water Consumption Anonymized**
dataset, together with derived and processed datasets used by the
forecasting and analysis workflows.

The dataset used during project development contains approximately:

-   **652,315 records**
-   **16 columns**
-   **214 sensors**
-   **28 apartments**
-   **9 clusters**
-   Approximately **10-minute** temporal resolution
-   Date range: **2019-12-31 to 2023-01-31**

The repository contains raw, processed, metadata, and evaluation files
used by the project.

### Data interpretation notes

-   The source dataset represents household/fixture-level observations
    from the HSB Living Lab; it is not live municipal network telemetry.
-   Interpret the `value` field using the source dataset documentation.
    Do not assume a unit conversion that has not been verified.
-   Missing observations are not automatically equivalent to zero
    consumption.
-   The `aggregated_value` field may represent cumulative meter
    readings; do not treat it as interval consumption without
    appropriate preprocessing.
-   Synthetic infrastructure, neighbourhood, reservoir, or shortage
    inputs used in simulations are scenario assumptions, not observed
    municipal measurements.

## Technology stack

  -----------------------------------------------------------------------
  Area                                Technologies
  ----------------------------------- -----------------------------------
  Application                         Python, Streamlit

  Data processing                     Pandas, NumPy

  Machine learning                    Scikit-learn, XGBoost

  Visualization                       Plotly, Matplotlib

  AI assistant                        Google Gemini API (`google-genai`
                                      Python SDK)

  Data and model artifacts            CSV datasets and serialized model
                                      artifacts
  -----------------------------------------------------------------------

The runtime dependencies are listed in
[`requirements.txt`](requirements.txt).

## Repository structure

``` text
AquaSentinel-AI/
├── app.py
├── requirements.txt
├── test_forecasting.py
├── .gitignore
├── .streamlit/
│   └── config.toml
├── data/
│   ├── raw/
│   ├── processed/
│   └── metadata/
├── evaluation/
├── models/
├── pages/
│   ├── 1_Overview.py
│   ├── Demand_Forecasting.py
│   ├── 3_Anomaly_Detection.py
│   ├── 4_Resource_Optimization.py
│   ├── 5_Crisis_Simulator.py
│   └── 6_AI_Agent.py
└── src/
    ├── models/
    ├── optimization/
    ├── preprocessing/
    ├── ui/
    └── analysis scripts
```

## Run locally

### Prerequisites

-   Python **3.12**
-   Git
-   A terminal (PowerShell, Command Prompt, or a Unix shell)

### 1. Clone the repository

``` bash
git clone https://github.com/Suhas2811/AquaSentinel_AI-Nxtwave_Hackathon.git
cd AquaSentinel_AI-Nxtwave_Hackathon
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

``` powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux**

``` bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

``` bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create `.streamlit/secrets.toml` in the project root:

``` toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Keep this file private. It is excluded by `.gitignore`; **never commit
API keys or other secrets to GitHub**.

### 5. Start the application

``` bash
streamlit run app.py
```

Streamlit will print a local URL in the terminal, usually
`http://localhost:8501`.

## Gemini API configuration

The AI Agent uses the Google GenAI Python SDK. For local development,
provide the key through Streamlit secrets as shown above. For Streamlit
Community Cloud, configure the same secret name in the app's **Settings
→ Secrets** panel:

``` toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Do not place the key directly in Python source code, README files,
screenshots, or public repository files. If a key is accidentally
exposed, revoke it and create a replacement.

## Forecasting validation

The repository includes `test_forecasting.py`, a standalone validation
script rather than a pytest test module. It loads the prepared test
dataset and trained forecasting models, computes per-sensor error
metrics, and prints overall MAE and RMSE.

Run it from the repository root after installing dependencies and
ensuring the referenced data and model artifacts are present:

``` bash
python test_forecasting.py
```

A validation run during project preparation reported:

-   **Overall Hybrid MAE:** `0.011619`
-   **Overall Hybrid RMSE:** `0.017949`
-   **Sensors evaluated:** `7`

These are results from a local validation run. They are dataset/model
evaluation results, not a guarantee of future performance or live
municipal forecasting accuracy.

## Limitations and responsible use

-   This is a prototype decision-support application, not a production
    water-management control system.
-   It does not ingest live municipal sensor feeds or control pumps,
    valves, reservoirs, or distribution networks.
-   Simulation results depend on selected assumptions and synthetic
    scenario inputs.
-   Anomaly detection flags patterns for investigation; it does not
    establish the cause of an event.
-   Forecast performance depends on the available historical data,
    preprocessing, and evaluation setup.
-   Dataset units, missingness, aggregation semantics, and
    representativeness should be checked before operational
    interpretation.
-   Allocation outputs are analytical recommendations for exploration,
    not legally binding or operational distribution instructions.

## Future improvements

-   Validate the data dictionary, measurement units, and aggregation
    semantics more fully.
-   Evaluate forecasting across additional sensors and time periods.
-   Add transparent fairness and essential-needs evaluation metrics.
-   Expand scenario testing with documented, realistic infrastructure
    assumptions.
-   Add data provenance and model-version reporting to the application.
-   Evaluate the system with domain experts and real operational
    stakeholders before any real-world use.

## Project links

-   **Live demo:** https://aquasentinel-ai-nxtwave.streamlit.app/
-   **GitHub:**
    https://github.com/Suhas2811/AquaSentinel_AI-Nxtwave_Hackathon

------------------------------------------------------------------------

*Built as a hackathon prototype for predictive urban water intelligence
and equitable resource-allocation decision support.*
