# Security Policy

## Supported versions

Security fixes are provided for the latest released version.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting for this repository. Do not open a public issue containing credentials, private endpoints, request bodies, or exploit details.

Include the affected version, impact, minimal reproduction, and suggested mitigation if known. Remove all live secrets before attaching logs.

## Credential policy

This project never needs a credential committed to source. Use a secret manager or protected service environment. If a real credential reaches Git history, revoke/rotate it first, then clean history; deleting the visible line is not sufficient.
