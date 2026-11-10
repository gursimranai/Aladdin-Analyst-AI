# 🧞 Aladdin Analyst AI

<p align="center">
  <strong>A modular, intelligent data analysis engine built to make working with data simpler, smarter, and more explainable.</strong>
</p>

<p align="center">
  From raw datasets to data quality, cleaning recommendations, and actionable insights — built one capability at a time.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-0.1.0-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Status-Active%20Development-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Tests-167%20Passing-success?style=for-the-badge" />
</p>

<p align="center">
  <a href="#-overview">Overview</a> •
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-roadmap">Roadmap</a>
</p>

---

## 🧭 Overview

**Aladdin Analyst AI** is an open-source Python project focused on building a modular and intelligent data analysis system.

The goal is to help users move from unfamiliar, raw datasets toward structured analysis and evidence-backed insights.

Rather than building an unrestricted AI agent from the beginning, Aladdin is being developed around a reliable analytical foundation:

```text
              RAW DATA
                  │
                  ▼
            DATA INGESTION
                  │
                  ▼
           DATA PROFILING
                  │
                  ▼
        DATA QUALITY ASSESSMENT
                  │
                  ▼
       CLEANING RECOMMENDATIONS
                  │
                  ▼
          AUTOMATED INSIGHTS
                  │
                  ▼
        CONFIGURABLE CLEANING
                  │
                  ▼
          FINAL DATA PROFILE
                  │
                  ▼
             ANALYSIS
```

The current implementation already provides the foundational workflow, while advanced analytical and AI capabilities remain part of the roadmap.

> **The vision is ambitious, but the implementation is incremental. Every feature should be functional, tested, and documented before being presented as complete.**

## ✨ Features

### Currently implemented

| Module | Capabilities | Status |
|---|---|---|
| Data Ingestion | CSV, Excel, JSON, Parquet | ✅ |
| Data Profiling | Dataset statistics, missing values, unique values, duplicates | ✅ |
| Quality Assessment | Missing values, constant columns, duplicate rows, structural issues | ✅ |
| Cleaning Engine | Configurable missing-value handling, duplicate removal, constant-column removal | ✅ |
| Recommendation Engine | Cleaning suggestions with priorities and approval requirements | ✅ |
| Insight Engine | Missing values, dominant categories, high cardinality, outliers, skewness | ✅ |
| Analysis Pipeline | Integrated profiling, quality, recommendations, insights, and cleaning | ✅ |
| Testing | Unit and integration test suite | ✅ |

### Development principles

- **Data integrity:** Preserve the original dataset during analysis and cleaning.
- **Controlled automation:** Make cleaning operations explicit and configurable.
- **Explainability:** Provide structured evidence behind recommendations and insights.
- **Modularity:** Keep components independent and reusable.
- **Reliability:** Validate behavior through automated tests.
- **Honest development:** Clearly distinguish implemented capabilities from future plans.

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/gursimranai/Aladdin-Analyst-AI.git

cd Aladdin-Analyst-AI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install the project

Install the package with development tools and optional Excel/Parquet support:

```bash
python -m pip install -e ".[dev,excel,parquet]"
```

### 4. Run your first analysis

```python
from aladdin import analyze_file

# Analyze a dataset
result = analyze_file("datasets/sample/sample_sales.csv")

# Initial dataset profile
print("Initial profile:")
print(result.initial_profile)

# Data quality
print("\nData quality:")
print(result.initial_quality_report)

# Cleaning recommendations
print("\nRecommendations:")
for recommendation in result.recommendations.recommendations:
    print(recommendation)

# Automated insights
print("\nInsights:")
for insight in result.insights.insights:
    print(insight)

# Final cleaned dataset
print("\nFinal dataset shape:")
print(result.dataframe.shape)
```

Aladdin returns a structured analysis result containing the initial profile, quality report, recommendations, insights, cleaning result, and final profile.

---

## 🏗️ Architecture

Aladdin follows a **modular monolith architecture**.

Each major capability has its own module, while the analysis pipeline coordinates the workflow.

```text
Aladdin-Analyst-AI/
│
├── src/
│   └── aladdin/
│       │
│       ├── ingestion/
│       │   ├── csv_loader.py
│       │   ├── excel_loader.py
│       │   ├── json_loader.py
│       │   └── parquet_loader.py
│       │
│       ├── profiling/
│       │   ├── models.py
│       │   └── profiler.py
│       │
│       ├── quality/
│       │   ├── models.py
│       │   └── assessor.py
│       │
│       ├── cleaning/
│       │   ├── models.py
│       │   └── cleaner.py
│       │
│       ├── recommendations/
│       │   ├── models.py
│       │   └── engine.py
│       │
│       ├── insights/
│       │   ├── models.py
│       │   └── engine.py
│       │
│       ├── pipeline/
│       │   ├── models.py
│       │   └── analyzer.py
│       │
│       ├── exceptions.py
│       ├── logging_config.py
│       └── __init__.py
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── examples/
├── datasets/
├── docs/
├── pyproject.toml
├── README.md
└── LICENSE
```

*This is a representative view of the implemented package structure, not an exhaustive file listing.*

### Analysis workflow

```text
                  INPUT DATA
                      │
                      ▼
                DATA INGESTION
                      │
                      ▼
               INITIAL PROFILE
                      │
                      ▼
              QUALITY ASSESSMENT
                      │
            ┌─────────┴─────────┐
            ▼                   ▼
      RECOMMENDATIONS     INSIGHT ENGINE
            │                   │
            └─────────┬─────────┘
                      ▼
               CLEANING ENGINE
                      │
                      ▼
                FINAL PROFILE
                      │
                      ▼
             FINAL QUALITY REPORT
                      │
                      ▼
               ANALYSIS RESULT
```

The original dataset is not modified by the analysis workflow. Cleaning operates on a separate working copy.

---

## 🧠 Core Components

### 1. Data Ingestion

Supports loading datasets from:

- CSV
- Excel (`.xlsx`)
- JSON
- Parquet

A unified loader dispatches files to the appropriate format-specific loader.

### 2. Data Profiling

Provides structured information about datasets, including:

- Dataset dimensions
- Column data types
- Missing-value counts and percentages
- Unique values
- Duplicate rows
- Numeric statistics
- Categorical summaries

### 3. Data Quality Assessment

Identifies potential data-quality problems:

- Missing values
- Duplicate rows
- Constant columns
- Empty datasets
- Duplicate column names

The assessment does not modify the original data.

### 4. Cleaning Engine

Supports explicitly configured operations:

- Keep missing values
- Drop rows containing missing values
- Fill missing values with a specified value
- Mean, median, and mode imputation
- Remove duplicate rows
- Remove constant columns

Cleaning produces a result and report rather than silently modifying the input.

### 5. Recommendation Engine

Analyzes data-quality issues and produces structured cleaning recommendations.

Each recommendation can include:

- Action
- Priority
- Affected column
- Estimated affected count
- Suggested strategy
- Approval requirement

Recommendations are separate from execution. They do not automatically apply cleaning operations.

### 6. Automated Insight Engine

Identifies patterns and observations using deterministic analytical rules.

Currently implemented:

- Missing-value observations
- Dominant categorical values
- High-cardinality columns
- Potential outliers using the IQR method
- Skewed numerical distributions

Insights include structured evidence and priority information.

> An observation is not automatically an explanation, prediction, or causal conclusion. Aladdin aims to keep these distinctions clear.

### 7. Analysis Pipeline

The pipeline connects the implemented components through two primary entry points:

```python
from aladdin import analyze_dataframe, analyze_file
```

- `analyze_dataframe()` analyzes an existing Pandas DataFrame.
- `analyze_file()` loads and analyzes a supported dataset file.

Both return an `AnalysisResult` containing the outputs of the workflow.

---

## 🧪 Testing & Code Quality

Reliability is a core part of the development process.

The project uses:

| Tool | Purpose |
|---|---|
| pytest | Automated testing |
| Ruff | Linting and formatting |
| Pandas | Data manipulation and analysis |
| setuptools | Python packaging |

Run the test suite:

```powershell
python -m pytest -q
```

Run lint checks:

```powershell
python -m ruff check src tests
```

Check formatting:

```powershell
python -m ruff format --check src tests
```

<details>
<summary><strong>Current verification</strong></summary>

- 167 tests passing
- Unit and integration tests
- Ruff lint checks passing
- Formatting checks passing

These results reflect the current development checkpoint and will evolve as new functionality is added.

</details>

---

## 🛣️ Roadmap

Aladdin is being developed in progressive milestones.

| Area | Status |
|---|---|
| Project foundation and packaging | ✅ Completed |
| Data ingestion | ✅ Implemented |
| Data profiling | ✅ Implemented |
| Data quality assessment | ✅ Implemented |
| Configurable cleaning | ✅ Implemented |
| Cleaning recommendations | ✅ Implemented |
| Automated data insights | ✅ Implemented |
| Correlation and relationship analysis | 🔄 Next |
| Advanced statistical analysis | 📅 Planned |
| Exploratory data analysis | 📅 Planned |
| Visualization engine | 📅 Planned |
| Reporting and exports | 📅 Planned |
| Machine-learning intelligence | 📅 Planned |
| Natural-language data analysis | 🔭 Future |
| Analyst agent and orchestration | 🔭 Future |

*The roadmap is flexible. Features will be introduced when their requirements, design, and implementation are ready.*

---

## 🔭 Long-Term Vision

The ultimate goal is to evolve Aladdin from a reliable data analysis library into a more intelligent analytical system.

Future capabilities may include:

### Intelligent analysis
- Dataset understanding and column-role detection
- Statistical and relationship analysis
- Context-aware analytical recommendations
- Anomaly detection
- Evidence-backed explanations

### Visualization and reporting
- Automatic chart recommendations
- Interactive dashboards
- Structured analytical reports
- Exportable results

### Machine learning
- Automated ML workflows
- Model evaluation
- Feature analysis
- Predictive analytics

### Natural-language intelligence
- Ask questions about datasets
- Generate analytical plans
- Execute controlled analytical operations
- Explain results in understandable language

### Analyst orchestration
- Coordinate analytical tools
- Validate intermediate results
- Support human approval
- Maintain reproducible workflows

These are long-term directions, not claims about currently available functionality.

---

## 🛡️ Data Integrity, Security & Privacy

The project is being designed around responsible data handling.

Key principles:

- Preserve original input data.
- Keep transformations explicit.
- Avoid unnecessary exposure of dataset contents in logs.
- Never commit API keys, credentials, or private datasets.
- Make external API usage explicit.
- Build toward reproducible and auditable analytical operations.

Future intelligent capabilities must operate within controlled execution boundaries.

---

## 🔬 Development Philosophy

Aladdin follows a research-driven engineering workflow:

```text
       RESEARCH
           │
           ▼
      UNDERSTAND
           │
           ▼
        DESIGN
           │
           ▼
     IMPLEMENT
           │
           ▼
         TEST
           │
           ▼
       EVALUATE
           │
           ▼
      DOCUMENT
           │
           ▼
       IMPROVE
```

The guiding principles:

1. **Data First** — Understand data before modifying it.
2. **Evidence Before Claims** — Insights must be supported by evidence.
3. **Controlled Automation** — Important actions should be explicit.
4. **Explainability** — Make analytical decisions understandable.
5. **Evaluation Before Trust** — Test features beyond a single example.
6. **Modularity** — Build reusable, maintainable components.
7. **Incremental Development** — Complete one capability before expanding.
8. **Honest Documentation** — Never present planned features as implemented.

---

## 🌱 Open Source & Contributions

Aladdin Analyst AI is intended to grow as an open-source project.

Potential contribution areas include:

- Data ingestion and connectors
- Profiling and quality assessment
- Cleaning algorithms
- Statistical methods
- Insight generation
- Visualization
- Machine learning
- Testing and benchmarks
- Documentation

Contributions, feedback, and engineering discussions are welcome.

Before contributing, please review the repository's contribution guidelines and code of conduct where available.

---

## 📌 Current Development Focus

**Current version:** `0.1.0`

**Current focus:** Building a reliable analytical foundation.

The next engineering milestone is **relationship and correlation analysis**, extending the insight engine beyond individual-column observations.

The priority remains simple:

Build reliable components first. Add intelligence on top of them.

---

## ⭐ The Goal

```text
              AN IDEA
                 │
                 ▼
          RELIABLE ENGINE
                 │
                 ▼
        INTELLIGENT ANALYSIS
                 │
                 ▼
        EVIDENCE-BASED INSIGHTS
                 │
                 ▼
         CONTROLLED AUTOMATION
                 │
                 ▼
          AI DATA ANALYST
```

Aladdin Analyst AI is being built one capability at a time.

Every feature should solve a real problem.

Every important result should have evidence.

Every milestone should improve the engineering quality of the project.

> **The vision can describe the future. The implementation must represent reality.**

---

## 📜 License

See [LICENSE](LICENSE) for licensing information.

---

<p align="center">
  <strong>🧞 Aladdin Analyst AI</strong>
  <br/>
  <sub>Turning raw data into meaningful understanding — one capability at a time.</sub>
</p>
