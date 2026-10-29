# Security Policy

## Reporting a vulnerability

Please do not report exploitable vulnerabilities in public issues. Contact the repository maintainer privately through GitHub's available security reporting feature, if enabled. Include the affected version or commit, impact, reproduction steps, and any safe proof of concept.

Please allow reasonable time to investigate and prepare a fix before public disclosure.

## Security design

RITS is intended to follow these principles:

- Keep API credentials out of source control.
- Store local secrets with Windows Credential Manager or an equivalent secure facility.
- Route all desktop actions through an allowlisted, validated task registry.
- Treat AI output and recognized speech as untrusted input.
- Require explicit confirmation for message sending and consequential actions.
- Use least privilege and restrict filesystem access.
- Fail safely on ambiguity, timeout, provider outage, or failed verification.

## Scope note

RITS is at the planning stage. Do not use it with sensitive accounts or automate consequential actions until the relevant feature has been implemented, reviewed, and tested.
