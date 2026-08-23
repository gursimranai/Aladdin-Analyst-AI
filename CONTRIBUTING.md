# Contributing to Aladdin Analyst AI

Thank you for your interest in contributing to **Aladdin Analyst AI**.

Aladdin Analyst AI is an early-stage open-source project. The project is currently focused on research, architecture, experimentation, and establishing a reliable engineering foundation.

Contributions are welcome, but please understand that the architecture may evolve as research progresses.

## 🧭 Before Contributing

Before implementing a major feature:

1. Read the `README.md`.
2. Review the relevant documentation in `docs/`.
3. Check the roadmap.
4. Search existing issues and pull requests.
5. Discuss major architectural changes before implementation.

Do not introduce large architectural changes without first understanding the existing design.

## 🔬 Research First

For research-heavy features, prefer:

```text
Research
   ↓
Experiment
   ↓
Evaluate
   ↓
Design
   ↓
Implement
   ↓
Test
   ↓
Document
```

Do not assume that a technically possible approach is automatically a good architectural choice.

## 🧱 Development Principles

Contributors should prioritize:

* Small, focused changes
* Clear interfaces
* Reproducibility
* Testing
* Documentation
* Data integrity
* Privacy
* Security
* Honest capability claims

Avoid creating large numbers of unused placeholder modules.

## 🌿 Branches

Use descriptive branch names.

Examples:

```text
feature/data-profiler
feature/csv-ingestion
feature/visualization-selector
fix/schema-detection
docs/architecture
research/automated-eda
```

## 💬 Commits

Use clear, descriptive commit messages.

Examples:

```text
feat(ingestion): add csv dataset loader
test(ingestion): add csv loader tests
docs(architecture): document data pipeline
research(profiling): evaluate dataset profiling approaches
fix(profiling): handle empty columns
```

## 🧪 Testing

New implementation should include appropriate tests.

Before submitting a pull request, verify that:

* Existing tests pass.
* New functionality is tested.
* Documentation is updated when necessary.
* No secrets or private datasets are included.

## 📊 Data and Datasets

Never commit private, sensitive, or unauthorized datasets.

When using public datasets, document:

* Source
* License
* Purpose
* Relevant preprocessing
* Known limitations

## 🔐 Security

Never commit:

* API keys
* Passwords
* Tokens
* Private credentials
* Sensitive datasets

For security issues, follow `SECURITY.md`.

## 📝 Documentation

If a change affects architecture, behavior, configuration, or usage, update the relevant documentation.

Important architectural decisions should be documented rather than existing only inside code or conversations.

## 🔄 Pull Requests

A pull request should explain:

### What changed?

Describe the implementation or research contribution.

### Why?

Explain the problem being solved.

### How?

Briefly describe the approach.

### Testing

Describe how the change was tested.

### Limitations

Clearly document known limitations or unresolved issues.

## 🤝 Code of Conduct

All contributors are expected to follow the project's `CODE_OF_CONDUCT.md`.

Thank you for helping build Aladdin Analyst AI.
