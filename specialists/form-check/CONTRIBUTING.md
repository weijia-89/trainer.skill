# Contributing, form-check.skill

This skill is a knowledge artifact, not a binary. Contributions extend it via well-shaped additions.

## Extension protocol

### Adding a new bug-class lens

1. Create `checklists/<your_lens>.md` with frontmatter:
   ```yaml
   ---
   name: <your_lens>
   version: <semver>
   parent_skill: form-check
   source: <citation tag from references/notes.md>
   ---
   ```
2. Use the established structure: introduction, walk (numbered items with question + sample defenses), cross-references, output format.
3. Add the lens to `checklists/INDEX.md` decision tree.
4. Update `checklists/bug_class_audit.md` with a cross-reference if the lens applies to a common surface.
5. Add citation tags to `references/notes.md` if new sources cited.
6. CHANGELOG entry in MINOR.

### Adding a new template

1. Create `templates/<your_template>.md` with frontmatter (`name`, `version`, `parent_skill`, `voice`, `note`).
2. Provide a fenced-code-block "template body" in markdown so users can copy-paste.
3. Document anti-patterns (what makes a template instance fail).
4. Cross-reference from any checklist or rubric that references it.
5. CHANGELOG entry.

### Adding a new language to multi-language matrix

1. Create `multi-language/<lang>.md` matching the established structure (tooling matrix, test-as-spec example, fitness-function example, common pitfalls, concurrency, build).
2. Update `multi-language/matrix.md` rows.
3. Update `rubrics/confidence_score.md` mutation-score targets.
4. CHANGELOG entry in MINOR.

### Adding a scale-up annex chapter

1. Confirm the chapter addresses a *forcing-constraint-class* problem (not a general best practice).
2. Create `scale-up/<chapter>.md` opening with the `[GATED, informational only]` watermark.
3. Document: when-to-activate criteria, default-mode alternative considered, the pattern, the cost dimensions, the sunset condition.
4. Update `scale-up/when_to_activate.md` TOC.
5. CHANGELOG entry in MINOR.

### Adding a citation

1. Verify primary source is accessible.
2. Add row to `references/notes.md` with tag, title, URL, verification date.
3. (Optional, historical) Cross-check against the upstream research dossier archived in a private local-only directory. That archive is no longer maintained; you do not need to update it.
4. Use the tag in skill content where applicable.
5. CHANGELOG entry in PATCH (citation-only) or MINOR (citation drives content).

## Quality bar

Before opening a PR:

- [ ] `tests/test_banned_vocab.sh` passes against new content
- [ ] `tests/test_self_voice.sh` passes
- [ ] `tests/test_citations.py` passes (no orphan tags)
- [ ] `tests/test_skill_format.sh` passes (frontmatter, line caps, required sections)
- [ ] `tests/test_rubric_arithmetic.py` passes if you touched a rubric
- [ ] CHANGELOG entry per SemVer rules
- [ ] No banned vocabulary outside `references/` / `examples/`
- [ ] All new claims have citation tags or `[normative, operator wisdom]`

## Posture preservation

This skill is **default-anti-enterprise** by design. Contributions adding microservices / k8s / event bus / CQRS content default-mode are rejected; such content belongs in the gated `scale-up/` annex.

Contributions that re-frame "operator wisdom" as "best practice" without empirical citation are downgraded to `[normative]` tags.

Contributions that increase the count of files agents must read at startup beyond what `SKILL.md`'s ≤220-line cap permits are restructured into lazy-loadable sub-files.

## Anti-contribution patterns

- "I think we should also include X" without a citation, ADR, or operator-wisdom tag, be explicit about which.
- Adding examples specific to one project (these belong in `examples/`, not in the canonical text).
- Drive-by additions of "trendy" technology without forcing-constraint analysis (rejected).
- Removing existing citations because "the URL changed" (instead, update the URL in references/notes.md and verify the tag still resolves).
- Reflexive substitution of one banned word with a synonym ("robust" → "powerful"), defeats the rule. Replace with a concrete property.

## Review process

PRs reviewed against:
- Confidence-score per-change ≥ tier-floor (per `rubrics/confidence_score.md`)
- Anti-pattern walk (`checklists/skill_antipatterns.md`)
- All skill self-tests passing
- CHANGELOG present

For substantive content additions: 2 reviewers + 1 ADR if it changes posture (e.g. modifying a refusal-list entry).

## License

By contributing, you agree your contribution is licensed under MIT (see `LICENSE`).
