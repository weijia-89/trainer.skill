# Negative fixture — should produce zero hits

This file uses precise vocabulary throughout. The system handles 1k requests per second at p99 of 180ms; tests run with mutation score above 75% on touched code; the deployment uses one platform-as-a-service in one region. We pin dependencies with hashes and verify each new package against the registry before adding it.

The architecture is a modular monolith. Decomposition would require a forcing-constraint ADR documenting which specific regulatory or measured-scale boundary the monolith fails to address. Until that ADR exists, the project ships as a single deployable.

Documentation tagged either with primary-source citations or with explicit `[normative]` markings. Reviewers compute confidence per change against the tier-floor matched to that change's reversibility class.

Tests cover acceptance criteria via failing-then-passing patterns. Property-based tests cover parsers and serializers. Integration tests use temporary directories and mock external dependencies only at the network boundary.

Supply-chain hygiene is mandatory: lockfiles include cryptographic hashes; vulnerability scanners run in continuous integration; software bill-of-materials generated per release.
