# RITS

**RITS is a local-first Windows desktop assistant for controlling workflows across apps—not just one messaging app.** It combines deterministic local automations with optional Gemini-powered intelligence and modular voice providers.

> **Project status:** Architecture and initial documentation are in place. Application implementation is next.

## Vision

RITS helps users work across Windows and supported applications through voice, text, shortcuts, and reusable workflows. It should remain useful when cloud AI is unavailable.

### Core principles

- **Local first:** Routine, predefined tasks run locally without Gemini API calls.
- **Cross-app by design:** Integrations are modular adapters, not hardcoded into the assistant core.
- **AI when useful:** Google Gemini API supports natural-language understanding, complex planning, and drafting.
- **Modular voice providers:** ElevenLabs and Fish Audio provide text-to-speech with configurable fallback.
- **Permission before action:** Actions are validated and consequential operations require explicit confirmation.
- **Security by design:** No committed secrets, no unrestricted shell execution, and least-privilege access.
- **Graceful failure:** Local features remain usable when internet access or cloud providers are unavailable.

## Planned capabilities

- Windows desktop interface, system tray, and keyboard shortcuts
- Local “Hey Rits” wake phrase and speech input/output
- Rule-based commands, timers, reminders, app launching, and custom workflows
- Gemini-powered conversations, task planning, and message/content drafting
- Cross-application integration framework for supported desktop apps and services
- File and folder search, clipboard helpers, and approved document workflows
- Optional messaging integrations (WhatsApp is one example, not the whole project)
- Configurable TTS providers, usage-aware fallback, and local settings/history

## Cross-app architecture

RITS uses a shared action registry and a common permission layer. Each application integration is a separate adapter, so adding one app should not require rewriting the core.

```text
Voice / Text / Keyboard Shortcut
              |
              v
        RITS Core Router
              |
      +-------+--------+
      |                |
      v                v
 Local Rules       Gemini API
 & Workflows       (optional cloud AI)
      |                |
      +-------+--------+
              |
              v
      Registered Task Registry
              |
              v
     Permission / Confirmation Gate
              |
              v
       Integration Adapters
       +------+-------+---------+
       |              |         |
     Windows        Files     App / Service
     controls       tools     integrations
                              (messaging,
                               browser, calendar)

TTS: ElevenLabs -> Fish Audio fallback -> optional local TTS
```

### Integration strategy

Prefer, in this order:
1. Official local or service APIs where available and appropriate.
2. Supported application command-line interfaces or documented extension interfaces.
3. Windows UI Automation for apps without suitable APIs, with visibility and verification.
4. Detect unsupported operations and explain limitations rather than pretending an action worked.

Each adapter should declare its capabilities, required permissions, supported actions, and whether it sends data off-device. RITS must not give Gemini direct unrestricted access to the operating system.

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
| Desktop automation | Restricted Windows UI Automation adapters |

Technology choices may be adjusted after compatibility checks and a minimal prototype.

## Development roadmap

1. **Foundation:** Repository structure, desktop shell, backend communication, logging, configuration, and secure credential storage.
2. **Local automation core:** Task registry, deterministic rules, app launching, timers, shortcuts, file search, and reusable workflows.
3. **Voice:** Local wake-word detection, speech recognition, TTS provider adapters, and graceful fallback.
4. **Gemini:** Conversation, intent understanding, task planning, and structured tool requests.
5. **Integration framework:** Common adapter interface, permission model, capability declarations, action verification, and integration tests.
6. **App integrations:** Add useful integrations based on API availability and testability. Messaging, browsers, calendars, productivity tools, and media apps can be evaluated as separate adapters.
7. **Hardening and release:** Security review, system tray, accessibility, Windows installer, documentation, and release process.

## Security requirements

- Never commit API keys, tokens, passwords, or personal data.
- Keep local secrets in Windows Credential Manager or an equivalent secure store.
- Use an allowlist of registered actions; never pass arbitrary AI output to a shell.
- Validate arguments, constrain filesystem access, and follow least privilege.
- Require explicit confirmation for sending messages, deleting or overwriting files, purchases, and other consequential actions.
- Verify outcomes after execution and report failures honestly.
- Use timeouts, cancellation, and safe behavior when providers or apps fail.
- Disclose when data is sent to cloud services and keep routine processing local when practical.

## Development status

This repository currently contains project documentation. Implementation will proceed in small, testable stages, beginning with the desktop shell and local automation engine.

## Contributing

Contributions and integration ideas are welcome as the project becomes runnable. Please do not submit secrets or personal data in issues or pull requests.

## License

RITS is intended to be released under the Apache License 2.0. See [LICENSE](LICENSE).
