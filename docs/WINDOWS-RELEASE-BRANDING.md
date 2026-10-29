# RITS Windows release branding

RITS Windows installers identify the publisher as **Nur Islam (DARKI)** and use [darki.online](https://darki.online) as the project homepage. The installer is configured for a current-user installation, an English-language NSIS wizard, and the RITS application icon for setup and uninstall.

## Code signing status

**Code signing is intentionally deferred.** Publisher metadata is descriptive metadata, not a digital signature. Until a trusted Windows code-signing certificate/service is configured and the release artifacts are signed, Windows may show an unknown-publisher or SmartScreen warning. Do not describe an unsigned build as signed or trusted.

## Before a public release

- Choose a legitimate code-signing provider and certificate appropriate for the release budget and distribution goals.
- Keep certificate files, passwords, tokens, and signing-service credentials out of Git; store them in GitHub Actions secrets or the provider's secret store.
- Configure signing only in the release workflow, and sign the final installer artifact (and any other distributed executable that requires it).
- Verify the signature and timestamp on the published artifact, and publish a SHA-256 checksum alongside the release.
- Build and test the installer on a clean Windows machine before announcing a release.

The installer metadata does not imply that the publisher identity has been independently verified.
