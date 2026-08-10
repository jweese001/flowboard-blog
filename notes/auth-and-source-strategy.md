# Auth and source strategy

This blog should not depend on a privileged interactive browser session.

Preferred evidence sources
1. Public repo history and docs in `/Users/jweese/code/flow-board`
2. Exported screenshots/assets committed or copied into this repo
3. A future FlowBoard journal/export surface designed for publication
4. A dedicated low-privilege service account, if account-backed inspection becomes necessary

What not to do
- Do not rely on your day-to-day Chrome login as the long-term cron auth path.
- Do not store your personal password in chat.
- Do not grant the blog pipeline write access to production user data unless explicitly needed.

If local credentials are needed later
- A local `.env` file is acceptable if it stays on disk and is not pasted into chat.
- Prefer a separate service account over your primary account.
- Prefer the smallest possible permissions.
- Pair credentials with an explicit read-only automation path.
