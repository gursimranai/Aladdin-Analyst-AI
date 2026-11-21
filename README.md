# 🧞 Aladdin Analyst AI

<p align="center">
  <strong>A modular Python data-analysis library for turning raw datasets into structured analysis, evidence-backed insights, and actionable cleaning recommendations.</strong>
</p>

<p align="center">
  <a href="https://github.com/gursimranai/Aladdin-Analyst-AI">
    <img src="https://img.shields.io/badge/Project-Aladdin%20Analyst%20AI-6C5CE7?style=for-the-badge" alt="Aladdin Analyst AI">
  </a>
  <img src="https://img.shields.io/badge/Version-0.1.0-2563EB?style=for-the-badge" alt="Version 0.1.0">
  <img src="https://img.shields.io/badge/Status-Active%20Development-F59E0B?style=for-the-badge" alt="Active development">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Tests-497%20Passing-16A34A?style=for-the-badge" alt="497 tests passing">
  <img src="https://img.shields.io/badge/License-Apache--2.0-0F766E?style=for-the-badge" alt="Apache 2.0 license">
</p>

<p align="center">
  <a href="#-overview">Overview</a> ·
  <a href="#-capabilities">Capabilities</a> ·
  <a href="#-quick-start">Quick start</a> ·
  <a href="#-architecture">Architecture</a> ·
  <a href="#-quality-and-testing">Quality & testing</a> ·
  <a href="#-roadmap">Roadmap</a>
</p>

---

## 🧭 Overview

**Aladdin Analyst AI** is an open-source Python project focused on building a modular, reliable, and extensible data-analysis library.

The project aims to help developers and data practitioners move from raw datasets to a structured understanding of their data through profiling, quality assessment, cleaning, recommendations, insights, visualization, and report generation.

The engineering approach is deliberate: establish a dependable analytical foundation before introducing machine-learning or language-model-driven automation.

### The analytical workflow

```text
                         INPUT DATA
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
                 ┌───────────┴───────────┐
                 ▼                       ▼
          RECOMMENDATIONS          INSIGHT ENGINE
                 │                       │
                 └───────────┬───────────┘
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
                    STRUCTURED ANALYSIS
                             │
                             ▼
                    REPORTING & EXPORTS
```

> **Development principle:** the vision can describe the future, but the implementation must represent what is actually built. Planned AI/LLM capabilities are not presented as current functionality.

---

## ✨ Capabilities

The following capabilities are implemented in the current development version.

| Component | Current capabilities |
|---|---|
| **Data ingestion** | CSV, Excel (`.xlsx`), JSON, and Parquet loaders, plus a unified format dispatcher |
| **Data profiling** | Dataset dimensions, data types, missing values, unique values, duplicates, numeric statistics, and categorical summaries |
| **Data quality** | Detection of missing values, duplicate rows, constant columns, empty datasets, and duplicate column names |
| **Cleaning engine** | Configurable missing-value handling, imputation, duplicate-row removal, and constant-column removal |
| **Recommendations** | Structured cleaning suggestions with action, priority, affected-column information, and approval requirements |
| **Insight engine** | Missing-value observations, dominant categories, high-cardinality columns, outlier detection, skewness, and numerical correlation analysis |
| **Analysis pipeline** | Coordinates profiling, quality assessment, recommendations, insights, cleaning, and final assessment |
| **Visualization** | Histograms, bar charts, missing-value charts, and correlation heatmaps |
| **Reporting** | JSON, HTML, and CSV report exports |
| **Package engineering** | Modular package structure, public API, build configuration, and optional dependency groups |

### Design principles

- **Data integrity:** analysis and cleaning should not silently mutate the caller's original DataFrame.
- **Controlled automation:** cleaning behavior is configurable; recommendations are separate from execution.
- **Evidence-backed insights:** analytical observations include structured evidence where applicable.
- **Explicit validation:** invalid inputs and unsupported configurations should fail clearly.
- **Modularity:** components are separated into focused, reusable modules.
- **Testability:** behavior is verified through unit and integration tests.
- **Honest scope:** implemented functionality is distinguished from the roadmap.

---

## 🚀 Quick start

### 1. Clone the repository

```bash
git clone https://github.com/gursimranai/Aladdin-Analyst-AI.git
cd Aladdin-Analyst-AI
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install the project

Install the package with its development tools and optional support for Excel, Parquet, and visualization:

```bash
python -m pip install -e ".[dev,excel,parquet,visualization]"
```

For a basic installation without optional features:

```bash
python -m pip install -e .
```

### 4. Run an analysis

```python
import pandas as pd

from aladdin import analyze_dataframe

data = pd.DataFrame(
    {
        "product": ["Laptop", "Mouse", "Keyboard", "Laptop", None],
        "price": [75000, 1200, 2500, 75000, 1800],
        "quantity": [2, 5, 3, 2, 4],
    }
)

result = analyze_dataframe(data)

# Initial dataset profile
print("Initial profile:")
print(result.initial_profile)

# Data-quality assessment
print("\nInitial data quality:")
print(result.initial_quality_report)

# Cleaning recommendations
print("\nRecommendations:")
for recommendation in result.recommendations.recommendations:
    print(recommendation)

# Automatically generated observations
print("\nInsights:")
for insight in result.insights.insights:
    print(insight)

# Result after the configured cleaning workflow
print("\nFinal dataset:")
print(result.dataframe)
```

The analysis returns an `AnalysisResult` containing the initial profile, initial quality report, recommendations, insights, cleaning result, final profile, and final quality report.

### Other entry points

```python
from aladdin import analyze_dataframe, analyze_file, load_csv, profile_data

# Load a CSV directly
dataframe = load_csv("path/to/data.csv")

# Profile an existing DataFrame
profile = profile_data(dataframe)

# Analyze an existing DataFrame
result = analyze_dataframe(dataframe)

# Load and analyze a supported file
file_result = analyze_file("path/to/data.csv")
```

Supported file extensions for the unified loader are `.csv`, `.xlsx`, `.json`, and `.parquet`.

---

## 🏗️ Architecture

Aladdin follows a **modular monolith architecture**. Each capability lives in a focused package, while the analysis pipeline coordinates the end-to-end workflow.

```text
Aladdin-Analyst-AI/
│
├── src/
│   └── aladdin/
│       ├── ingestion/
│       │   ├── csv_loader.py
│       │   ├── excel_loader.py
│       │   ├── json_loader.py
│       │   ├── parquet_loader.py
│       │   └── loader.py
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
│       ├── visualization/
│       │   ├── config.py
│       │   ├── engine.py
│       │   └── models.py
│       │
│       ├── reporting/
│       │   ├── exporter.py
│       │   └── models.py
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

*This is a high-level view of the package structure, not an exhaustive listing of every project file.*

### Separation of responsibilities

| Layer | Responsibility |
|---|---|
| Ingestion | Read supported file formats into Pandas DataFrames |
| Profiling | Summarize dataset and column characteristics |
| Quality | Identify structural and data-quality issues |
| Recommendations | Convert detected issues into suggested actions |
| Cleaning | Apply explicitly configured data-cleaning operations |
| Insights | Generate deterministic, evidence-oriented observations |
| Pipeline | Coordinate the analysis stages and package their results |
| Visualization | Create charts from dataset characteristics |
| Reporting | Serialize analysis outputs into exportable reports |

The pipeline keeps the original input DataFrame separate from the working data used for cleaning. Recommendations are generated independently and are not silently executed.

---

## 🔍 Core components

### 1. Data ingestion

Format-specific loaders support:

- CSV
- Excel (`.xlsx`)
- JSON
- Parquet

A unified `load_data()` function selects a loader based on the file extension. Loader-specific keyword arguments are forwarded to the corresponding Pandas reader.

### 2. Data profiling

The profiler produces structured dataset and column summaries, including:

- Row and column counts
- Column data types
- Missing-value counts and percentages
- Unique-value counts and percentages
- Duplicate-row counts
- Numeric descriptive statistics
- Frequent categorical values

### 3. Data quality assessment

The quality assessor identifies issues such as:

- Missing values
- Duplicate rows
- Constant columns
- Empty datasets
- Duplicate column names

The assessment reports issues without modifying the input DataFrame.

### 4. Cleaning engine

The cleaning engine supports configurable operations, including:

- Keeping missing values
- Dropping rows containing missing values
- Filling missing values with a specified value
- Mean, median, and mode imputation where applicable
- Removing duplicate rows
- Removing constant columns

Cleaning returns a structured result and report. It does not silently modify the original input.

### 5. Cleaning recommendation engine

The recommendation engine translates supported data-quality issues into structured recommendations.

A recommendation can include:

- Recommended action
- Priority
- Affected column
- Affected-record count
- Suggested missing-value strategy
- Whether approval is required

Recommendations and cleaning execution remain separate steps.

### 6. Insight engine

The current deterministic insight engine identifies:

- Missing-value patterns
- Dominant categorical values
- High-cardinality columns
- Potential numerical outliers using the IQR method
- Skewed numerical distributions
- Strong numerical correlations

Insights include category, priority, and structured evidence.

> An observed pattern is not automatically an explanation, prediction, or causal conclusion. Aladdin aims to keep those distinctions explicit.

### 7. Analysis pipeline

The main pipeline entry points are:

```python
from aladdin import analyze_dataframe, analyze_file
```

- `analyze_dataframe()` analyzes an existing Pandas DataFrame.
- `analyze_file()` loads a supported dataset file and analyzes it.

Both return an `AnalysisResult` containing the outputs of the workflow.

### 8. Visualization engine

Current chart types:

- Histograms
- Bar charts
- Missing-value charts
- Correlation heatmaps

Visualization configuration supports chart dimensions, output format, display behavior, and saving charts.

### 9. Reporting and exports

Analysis reports can be exported in:

- **JSON** — structured machine-readable output
- **HTML** — standalone human-readable report
- **CSV** — flattened report data

The reporting layer provides structured report configuration and export results.

---

## 🧪 Quality and testing

Testing is a core part of the development process. The project uses automated tests to verify behavior, edge cases, validation rules, and regressions across its modules.

### Current verification checkpoint

<p align="center">
  <img src="https://img.shields.io/badge/Latest%20reported%20test%20run-497%20passed-16A34A?style=for-the-badge&logo=pytest&logoColor=white" alt="497 tests passed">
</p>

The latest full-suite result reported during development was **497 passed**. This is a development checkpoint, not a claim that the project is finished. The count may change as implementation and regression tests evolve.

### Development tools

| Tool | Purpose |
|---|---|
| pytest | Unit and integration testing |
| Ruff | Linting and formatting |
| Coverage.py | Test coverage measurement |
| Pandas | Tabular data operations |
| NumPy | Numerical operations |
| setuptools | Package build system |

Run the test suite:

```bash
python -m pytest -q
```

Run lint checks:

```bash
python -m ruff check .
```

Check formatting:

```bash
python -m ruff format --check .
```

Build the distributions (if the `build` package is installed):

```bash
python -m build
```

---

## 🛣️ Roadmap

Aladdin is being developed incrementally. The roadmap distinguishes implemented functionality from areas that still require design and development.

| Area | Status |
|---|---|
| Project foundation and package structure | ✅ Implemented |
| Package metadata and distribution builds | ✅ Implemented |
| CSV, Excel, JSON, and Parquet ingestion | ✅ Implemented |
| Data profiling | ✅ Implemented |
| Data quality assessment | ✅ Implemented |
| Configurable data cleaning | ✅ Implemented |
| Cleaning recommendations | ✅ Implemented |
| Deterministic insight generation | ✅ Implemented |
| Numerical correlation analysis | ✅ Implemented |
| Analysis pipeline | ✅ Implemented |
| Visualization engine | ✅ Implemented |
| JSON, HTML, and CSV reporting | ✅ Implemented |
| Broader exploratory data analysis workflows | 📅 Planned |
| Advanced statistical analysis | 📅 Planned |
| Expanded analytical and visualization capabilities | 📅 Planned |
| Machine-learning-assisted analysis | 🔭 Future |
| Natural-language dataset interaction | 🔭 Future |
| Controlled analyst-agent orchestration | 🔭 Future |

The roadmap may change as requirements are evaluated and implementation progresses.

---

## 🔭 Long-term direction

The long-term goal is to evolve Aladdin from a dependable data-analysis library into a more capable intelligent analytical system.

Potential future directions include:

**Intelligent analysis**
- Dataset and column-role understanding
- Context-aware analytical recommendations
- More advanced statistical analysis
- Anomaly detection
- Evidence-backed explanations

**Visualization and reporting**
- Automatic chart recommendations
- Expanded report customization
- Interactive dashboards
- More export formats

**Machine learning**
- Automated ML workflows
- Model evaluation
- Feature analysis
- Predictive analytics

**Natural-language interaction**
- Ask questions about datasets
- Generate analytical plans
- Execute controlled analytical operations
- Explain results in accessible language

**Analyst orchestration**
- Coordinate analytical tools
- Validate intermediate results
- Support human approval
- Maintain reproducible workflows

These are future directions, not claims about currently available functionality. AI/LLM capabilities will be considered after the analytical foundation is sufficiently reliable and evaluated.

---

## 🛡️ Data integrity and responsible development

The project is being developed around a few important principles:

- Preserve original input data during analysis.
- Keep transformations explicit and configurable.
- Separate recommendations from execution.
- Avoid unnecessary exposure of dataset contents in logs.
- Never commit API keys, credentials, or private datasets.
- Make external service usage explicit.
- Aim for reproducible and auditable analytical operations.

Future intelligent capabilities should operate within clear validation and execution boundaries.

---

## 🧠 Development philosophy

The project follows an iterative engineering workflow:

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

Guiding principles:

1. **Data first** — understand data before modifying it.
2. **Evidence before claims** — insights should be supported by data.
3. **Controlled automation** — important actions should be explicit.
4. **Explainability** — make analytical decisions understandable.
5. **Evaluation before trust** — test beyond a single happy path.
6. **Modularity** — build focused, reusable components.
7. **Incremental development** — strengthen each capability before expanding.
8. **Honest documentation** — never present planned features as implemented.

---

## 🌱 Open source and contributions

Aladdin Analyst AI is intended to grow as an open-source project.

Areas where future contributions and feedback may be useful include:

- Data ingestion and connectors
- Profiling and quality assessment
- Cleaning strategies
- Statistical methods
- Insight generation
- Visualization and reporting
- Testing and benchmarks
- Documentation

Feedback, issue reports, and engineering discussions are welcome. Please review the repository's contribution guidelines and code of conduct if and when they are available.

---

## 📌 Project status

| Detail | Current information |
|---|---|
| Project | Aladdin Analyst AI |
| Package version | `0.1.0` |
| Python requirement | `3.11+` |
| Development status | Active development |
| Latest reported full-suite result | `497 passed` |
| License | Apache License 2.0 |
| Primary language | Python |

**Current engineering priority:** continue strengthening the implemented analytical foundation, validate edge cases, and improve the consistency of the public APIs before expanding into more advanced intelligence.

---

## 📜 License

This project is licensed under the **Apache License 2.0**. See [`LICENSE`](LICENSE) for details.

---

<p align="center">
  <strong>🧞 Aladdin Analyst AI</strong>
  <br>
  <sub>Turning raw data into meaningful understanding — one capability at a time.</sub>
  <br><br>
  <a href="https://github.com/gursimranai/Aladdin-Analyst-AI">Explore the repository</a>
</p>
