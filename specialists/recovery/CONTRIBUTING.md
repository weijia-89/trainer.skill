# Contributing, recovery.skill

This skill is a *workflow* layer over `form-check.skill`. Contributions usually fall into one of these patterns.

## Extension patterns

### Adding a new phase to the DAG

1. Edit `workflow/workflow_dag.md` (canonical), add phase node + edges + activation criteria.
2. Add the phase prompt in `workflow/phase_prompts.md` (env-agnostic, parameterized).
3. Update `SKILL.md` Section 1 phase list.
4. Update `checklists/launch_ready.md` if the phase contributes to DoD.
5. Update `rubrics/code_fixer_confidence.md` if the phase contributes a new component.
6. Add a smoke test referencing the phase.
7. CHANGELOG entry in MINOR.

### Adding an adversarial question

1. Edit `workflow/adversarial_questions.md` (renumber if inserting; or append).
2. Cross-reference to relevant checklists in `form-check`.
3. CHANGELOG entry in MINOR.

### Tweaking deAI rules

- Adding a banned word: edit `templates/deai_rules.md` regex; update `tests/test_deai_regex.py` fixtures (positive case must include the new word; negative must not).
- Adding an archetype overlay: section in `templates/deai_rules.md`; corresponding section in `templates/doc_voice.md`; fixture pair.
- CHANGELOG entry: PATCH (typo / equivalence) or MINOR (new archetype / new word that flags previously-passing content).

### Bumping the `form-check` composes pin

- Update `SKILL.md` frontmatter `composes` block.
- Verify referenced files exist with declared version (`tests/test_skill_version_compat.py`).
- If `form-check` MAJOR change: recovery MAJOR.
- If `form-check` MINOR change: recovery MINOR (review for behavioral changes).
- If `form-check` PATCH: recovery PATCH (rebuild docs reference if needed).

## Quality bar

- All skill self-tests pass.
- DAG diagram matches `workflow/workflow_dag.md` canonical (no drift across files).
- Per-archetype voice rules respected in any prose this PR adds.
- CHANGELOG entry per SemVer rules.

## Anti-contribution patterns

- Adding a phase without activation criteria, leads to "always run" waterfall drift.
- Duplicating content from `form-check` instead of referencing, composition over duplication is the design rule.
- Hardcoding paths in phase prompts, they must be parameterized.
- Adding voice rules at the file level instead of the archetype level, defeats the segregation.

## Review process

Same as `form-check.skill/CONTRIBUTING.md` quality bar. Substantive workflow changes require an ADR.

## License

MIT.
