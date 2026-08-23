# Security Policy

## 🔐 Aladdin Analyst AI Security

Security and privacy are important considerations for Aladdin Analyst AI, particularly because future versions may process user-provided datasets.

The project is currently in an early research and architecture stage.

## ⚠️ Current Status

Aladdin Analyst AI is not currently a production-ready data-analysis platform.

Do not use unreleased or experimental components with sensitive, confidential, or production-critical data unless their security properties have been independently evaluated.

## Reporting a Vulnerability

Please do **not** publicly disclose security vulnerabilities through GitHub issues.

Instead, report security concerns privately to the project maintainers.

When reporting a vulnerability, provide:

* A description of the issue
* Steps to reproduce it
* Potential impact
* Affected component or version
* Any relevant logs or proof of concept that can be safely shared

Please avoid including secrets, credentials, private datasets, or personally identifiable information in reports.

## Security Principles

As the project evolves, security considerations will include:

* Secure secret management
* Protection of API credentials
* Privacy-aware logging
* PII awareness
* Controlled tool execution
* Dataset isolation
* Access control
* Data deletion
* Auditability
* Safe external API usage

## Never Commit Secrets

Never commit:

```text
API keys
Passwords
Access tokens
Private credentials
Private datasets
Production secrets
```

Use environment variables or an appropriate secret-management system instead.

## Dataset Privacy

Users and contributors should avoid committing sensitive datasets to the repository.

Public datasets should have their source and license documented.

## Experimental Features

Experimental AI, LLM, agent, or code-execution features should be treated as potentially unsafe until properly evaluated.

Security claims should be based on testing and evidence rather than assumptions.

## Future Updates

This policy will be updated as Aladdin Analyst AI moves from research and experimentation toward production-ready components.
