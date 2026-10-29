# RITS

**RITS is a local-first Windows desktop AI assistant.** It combines dependable rule-based automations with optional cloud intelligence, giving you a useful assistant even when AI services are unavailable.

> **Project status:** Architecture finalized; initial implementation not yet started.

## Vision

RITS is designed to help users interact with Windows through voice and text, automate repeatable tasks, and use AI where it adds value—without making the entire application dependent on an AI provider.

### Core principles

- **Local first:** Routine, predefined automations run locally without Gemini API calls.
- **AI when useful:** Google Gemini API supports natural-language understanding, complex planning, and message drafting.
- **Modular voice providers:** ElevenLabs and Fish Audio provide text-to-speech, with configurable fallback behavior.
- **Permission before action:** Every desktop action is validated. Sending messages and other consequential actions require explicit confirmation.
- **Security by design:** No committed secrets, no unrestricted shell execution, and least-privilege integrations.
- **Graceful failure:** Local features remain usable when internet access or cloud providers are unavailable.

## Planned capabilities

- Windows desktop interface with system-tray support
- Local wake phrase: “Hey Rits”
- Speech input and spoken responses
- Local command rules and customizable shortcuts
- Timers, reminders, simple utilities, and approved workflows
- Gemini-powered conversations, task planning, and message drafting
- Optional WhatsApp Desktop integration
- Provider selection, fallback, and usage-aware voice output
- Local settings and conversation history

## Architecture

```text
Voice / Text / Shortcut
          |
          v
     RITS Core Router
          |
    +-----+------+
    |            |
    v            v
Local rules    Gemini API
& workflows    (optional cloud intelligence)
    |            |
    +-----+------+
          |
          v
Security & Permission Gate
          |
          v
Registered Windows Actions / Integrations

TTS providers: ElevenLabs -> Fish Audio fallback -> optional local TTS
```

The local automation engine handles deterministic tasks first. Gemini may request registered tools, but it does not execute them directly or bypass RITS permissions.

## Planned technology

| Layer | Technology |
| --- | --- |
| Desktop shell | Tauri 2 |
| UI | React + TypeScript |
| Local backend | Python |
| Cloud intelligence | Google Gemini API |
| Text-to-speech | ElevenLabs and Fish Audio |
| Wake-word detection | Local |
| Speech recognition | Local-first; optional cloud fallback |
| Local data | SQLite |
| Credential storage | Windows Credential Manager |
| Windows automation | Windows UI Automation with restricted adapters |

Technology choices may be adjusted after compatibility checks and a minimal prototype.

## Development roadmap

1. **Foundation:** Repository layout, desktop shell, backend communication, configuration, structured logging, and secure credential storage.
2. **Local automation:** Command router, task registry, rules, shortcuts, timers, and predefined workflows.
3. **Voice:** Local wake-word detection, speech recognition, TTS provider adapters, and graceful fallback.
4. **Gemini:** Model configuration, conversation, intent handling, tool requests, and message drafting.
5. **Desktop integrations:** Restricted app launching and a safe WhatsApp draft-and-confirm workflow.
6. **Hardening and release:** Automated tests, security review, system tray, installer, documentation, and release process.

## Security requirements

- Never commit API keys, access tokens, passwords, or personal data.
- Keep local secrets in Windows Credential Manager or another appropriate secure store.
- Use an allowlist of registered actions; never pass arbitrary Gemini output to a shell.
- Validate tool arguments and constrain file access.
- Require explicit confirmation before sending messages or performing consequential actions.
- Use timeouts, safe cancellation, and clear errors for cloud provider failures.
- Do not claim an action succeeded until its result is verified.
- Keep routine processing local whenever practical; disclose when data is sent to cloud services.

## Development status

This repository currently documents the project vision and architecture. The implementation will be developed in small, testable stages, starting with the desktop shell and local automation engine.

## Contributing

Contributions, bug reports, and design discussions will be welcome as the project becomes runnable. Please do not submit secrets or personal data in issues or pull requests.

## License

RITS is intended to be released under the Apache License 2.0. See [LICENSE](LICENSE).
