---
name: investment-onboarding
description: Onboard an August teammate into the shared Investment Brain and create or update only their authenticated Azure investment profile. Use when someone says onboard me, set up my Investment Brain, configure my investment profile, or redo investment onboarding. This does not create a local general-purpose Personal Brain, builder, thinker, diary, or worldview memory.
---

# Investment onboarding

Resolve ../investment-brain/scripts/brain_api.py relative to this SKILL.md, never relative to the user's working directory.

Create a compact investment-working profile through the authenticated API. Ask one question at a time and keep the conversation under fifteen minutes.

1. If the user explicitly asks to reset or redo onboarding from scratch, first run `python ../investment-brain/scripts/brain_api.py profile reset`. Then silently run `python ../investment-brain/scripts/brain_api.py profile get`.
   - If a completed profile exists, explain that this is an update and preserve fields the user does not change.
   - If authentication fails, stop. Never collect profile answers that cannot be saved securely.
2. Briefly explain that August Company/Org memory is shared, while this profile changes presentation and workflow only. It does not restrict what shared Brain evidence the user may read.
3. Ask:
   - Name and August role.
   - Seat or primary responsibility: directs, funds, operations, or another description.
   - Coverage and recurring work.
   - Preferred answer depth and bullets-versus-prose format.
   - Working rules the agent should always or never follow.
   - Main tools and recurring outputs.
   - Anything an investment agent should always keep in mind.
4. Reflect the compact profile and ask for confirmation before the durable write.
5. Submit one JSON object with:
   `python ../investment-brain/scripts/brain_api.py profile onboard --json '<profile>'`
   Allowed fields are `display_name`, `email`, `role_title`, `seat`, `coverage`, `answer_preferences`, `working_preferences`, `tools_outputs`, and `always_keep_in_mind`.
6. Confirm that the profile is stored under the authenticated identity and will be shared across supported Investment Brain clients. Do not create local diary, worldview, builder, thinker, or writing files.
7. Offer to install the auto-routing rule (recommended; one yes/no question). On yes, append the marked block below to the user's global agent instructions file — `~/.claude/CLAUDE.md` in Claude Code, `~/.codex/AGENTS.md` in Codex — creating the file if it does not exist. If a block with the same markers is already present, replace that block in place instead of appending a duplicate. Never modify anything outside the markers, and never remove or rewrite the user's own instructions or personal memory setup.

   ```markdown
   <!-- august-investment-brain-routing:start (managed by investment-onboarding) -->
   # August Investment Brain routing
   - When a question touches August's investments — the portfolio, the book, a portfolio company, a deal, a fund, diligence, prior views, or team positions — use the `investment-brain` skill automatically. Never wait for the words "use the investment brain."
   - This rule claims August firm questions only. Personal memory systems ("personal brains"), personal-portfolio skills, and private notes keep owning personal context — when a question is about the user's own money, memory, or workflows, defer to those.
   - When both matter, compose: personal context from the user's own system, August evidence from the Investment Brain, kept separate and cited.
   <!-- august-investment-brain-routing:end -->
   ```

Never accept or send a `principal`, `user_id`, or another person's identity. The backend owns identity selection.
