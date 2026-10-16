# Development instructions

Read README.md and docs/01-confirmed-design.md before editing. The JSON requirements are a design contract, not implemented game code. Later direct user instructions take precedence.

- Preserve all user-confirmed rules, especially gray population removal, all non-elite jobs, 3–6 month filling, white-only leaders, and combined genetic/psionic progression.
- Do not reintroduce surplus resettlement, reserve jobs, or population loss as merely a metaphor. Surplus gray population is actually removed by the intended game rule.
- Steel Mosquito civilization begins as white mosquitoes plus robots and pursues synthetic ascension. Do not write the superseded story of gray mosquitoes collectively transforming into machines.
- Keep the original Syncretic Evolution start. Resolve its employment constraints specifically for Haipam rather than globally changing other civilizations without justification.
- Confirm the target Stellaris version and DLC before writing version-dependent script. Neither local script parsing nor this handoff validator proves gameplay correctness.
- Separate user requirements from assistant-proposed balance figures; see docs/05-proposals-and-open-questions.md.
- Preserve Haipam's strong gameplay direction: normal economic development, ability to contest the Great Khan, exceptional late production. Do not quietly substitute an ordinary balanced flavor pack.
- User rejected adding assorted canonical military units simply to increase content volume. They are optional source references, not approved scope.
- Do not report generated models as integrated models; test scale, materials, locators, motion and firing in the actual game.
- Repository target is mohsunil/qunxing. User initially requested private hosting, then explicitly authorized uploading this handoff to this PUBLIC repository on 2026-10-16. Do not reuse an unrelated repository.
- Never commit keys, credentials, browser sessions, raw personal logs, or proprietary base-game assets. Use source references for assets not included in this package.
- Do not modify memories without a direct user request. Do not create a new chat or message another chat unless explicitly asked.
- No sub-agent delegation unless directly authorized by the user or applicable higher-level instructions.

The initial design handoff is preserved in the v0.1.0 release. mod/haipam now contains v0.2.0-alpha source; it is not yet engine-validated. Read docs/09-prototype-progress.md before changing runtime scripts. scripts/install_mod.py generates a local rules adapter from the user's installed 4.5.2 game; never commit or package that generated adapter or copy proprietary base-game assets. Local install reports/backups are excluded from publication.

