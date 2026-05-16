#!/usr/bin/env python3
"""Mutation-equivalent coverage for blast_radius.py.

Aims: kill the obvious arithmetic and pattern mutations that a basic
fuzz / cosmic-ray pass would generate.

Covers:
  - privilege_for: every PRIVILEGE_PATTERN row + first-match precedence
  - env_var_bonus: every supported runtime pattern + multi-file early exit
  - compute: empty-diff short-circuit + score clamp + arithmetic shape
  - call_paths_estimate: empty input + irrelevant-extension filter
  - CLI main: non-existent path -> exit 2
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

# Add the tools dir to import path
SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "tools"))

import blast_radius  # type: ignore


# ---------- privilege_for ----------

def test_privilege_internal_for_unmatched() -> None:
    label, weight = blast_radius.privilege_for(Path("src/utils/format.py"))
    assert (label, weight) == ("internal", 5), f"got ({label},{weight})"


def test_privilege_public_api() -> None:
    label, weight = blast_radius.privilege_for(Path("src/api/users.py"))
    assert (label, weight) == ("public-api", 30), f"got ({label},{weight})"


def test_privilege_public_dir() -> None:
    label, weight = blast_radius.privilege_for(Path("public/index.html"))
    assert (label, weight) == ("public-api", 30), f"got ({label},{weight})"


def test_privilege_write_effect_db() -> None:
    label, weight = blast_radius.privilege_for(Path("src/db/users.py"))
    assert (label, weight) == ("write-effect", 30), f"got ({label},{weight})"


def test_privilege_write_effect_migrations() -> None:
    label, weight = blast_radius.privilege_for(Path("backend/migrations/2026_05_14_add_users.sql"))
    assert (label, weight) == ("write-effect", 30), f"got ({label},{weight})"


def test_privilege_write_effect_schema() -> None:
    label, weight = blast_radius.privilege_for(Path("src/schema/v2.py"))
    assert (label, weight) == ("write-effect", 30), f"got ({label},{weight})"


def test_privilege_secret_handling_via_path() -> None:
    label, weight = blast_radius.privilege_for(Path("src/auth/token.py"))
    assert (label, weight) == ("secret-handling", 30), f"got ({label},{weight})"


def test_privilege_secret_handling_via_filename_password() -> None:
    label, weight = blast_radius.privilege_for(Path("src/utils/password_hash.py"))
    assert (label, weight) == ("secret-handling", 30), f"got ({label},{weight})"


def test_privilege_secret_handling_via_filename_secret() -> None:
    label, weight = blast_radius.privilege_for(Path("src/utils/secret_store.py"))
    assert (label, weight) == ("secret-handling", 30), f"got ({label},{weight})"


def test_privilege_secret_handling_via_filename_token() -> None:
    label, weight = blast_radius.privilege_for(Path("src/utils/refresh_token.py"))
    assert (label, weight) == ("secret-handling", 30), f"got ({label},{weight})"


def test_privilege_secret_handling_via_filename_crypto() -> None:
    label, weight = blast_radius.privilege_for(Path("src/utils/crypto_helpers.py"))
    assert (label, weight) == ("secret-handling", 30), f"got ({label},{weight})"


def test_privilege_admin_write_effect() -> None:
    label, weight = blast_radius.privilege_for(Path("src/admin/users.py"))
    assert (label, weight) == ("write-effect", 25), f"got ({label},{weight})"


def test_privilege_styles_internal_css() -> None:
    label, weight = blast_radius.privilege_for(Path("src/components/Button.css"))
    assert (label, weight) == ("internal", 5), f"got ({label},{weight})"


def test_privilege_styles_internal_scss() -> None:
    label, weight = blast_radius.privilege_for(Path("src/styles/theme.scss"))
    assert (label, weight) == ("internal", 5), f"got ({label},{weight})"


def test_privilege_styles_dir() -> None:
    label, weight = blast_radius.privilege_for(Path("frontend/style/colors.ts"))
    assert (label, weight) == ("internal", 5), f"got ({label},{weight})"


def test_privilege_docs_md() -> None:
    label, weight = blast_radius.privilege_for(Path("docs/architecture.md"))
    assert (label, weight) == ("internal", 5), f"got ({label},{weight})"


def test_privilege_docs_dir() -> None:
    label, weight = blast_radius.privilege_for(Path("doc/guide.txt"))
    assert (label, weight) == ("internal", 5), f"got ({label},{weight})"


def test_privilege_md_extension_anywhere() -> None:
    # Any .md file is treated as docs (internal); README.md at root counts.
    label, weight = blast_radius.privilege_for(Path("README.md"))
    assert (label, weight) == ("internal", 5), f"got ({label},{weight})"


def test_privilege_first_match_wins_api_over_admin() -> None:
    # PRIVILEGE_PATTERNS ordering: api/public-api comes before admin/write-effect.
    # A path matching both should resolve to the first match (public-api).
    label, weight = blast_radius.privilege_for(Path("src/api/admin/users.py"))
    assert (label, weight) == ("public-api", 30), f"got ({label},{weight}) — first-match precedence broke"


def test_privilege_secret_keyword_beats_internal() -> None:
    # /docs/ would match internal (5), but 'token' substring earlier overrides because
    # secret-handling row is earlier in PRIVILEGE_PATTERNS.
    label, weight = blast_radius.privilege_for(Path("docs/access_token_design.md"))
    # First match wins; secret-handling is row 3; docs is row 6.
    assert (label, weight) == ("secret-handling", 30), f"got ({label},{weight})"


# ---------- env_var_bonus ----------

def test_env_var_bonus_zero_for_clean_file(tmp_path: Path) -> None:
    p = tmp_path / "clean.py"
    p.write_text("def f():\n    return 1 + 2\n")
    assert blast_radius.env_var_bonus([p]) == 0


def test_env_var_bonus_python_os_environ(tmp_path: Path) -> None:
    p = tmp_path / "config.py"
    p.write_text("import os\nFOO = os.environ['FOO']\n")
    assert blast_radius.env_var_bonus([p]) == 20


def test_env_var_bonus_python_getenv(tmp_path: Path) -> None:
    p = tmp_path / "config.py"
    p.write_text("from os import getenv\nFOO = getenv('FOO')\n")
    assert blast_radius.env_var_bonus([p]) == 20


def test_env_var_bonus_node_process_env(tmp_path: Path) -> None:
    p = tmp_path / "config.js"
    p.write_text("const FOO = process.env.FOO;\n")
    assert blast_radius.env_var_bonus([p]) == 20


def test_env_var_bonus_java_system_getenv(tmp_path: Path) -> None:
    p = tmp_path / "Config.java"
    p.write_text("String foo = System.getenv(\"FOO\");\n")
    assert blast_radius.env_var_bonus([p]) == 20


def test_env_var_bonus_php_env_brackets(tmp_path: Path) -> None:
    p = tmp_path / "config.php"
    p.write_text("$foo = $_ENV['FOO']; // or env['FOO']\n")
    assert blast_radius.env_var_bonus([p]) == 20


def test_env_var_bonus_early_exit(tmp_path: Path) -> None:
    """If ANY file has an env-var pattern, bonus is 20 (not summed)."""
    clean = tmp_path / "clean.py"
    clean.write_text("def f(): pass\n")
    dirty = tmp_path / "dirty.py"
    dirty.write_text("import os\nFOO = os.environ['FOO']\n")
    assert blast_radius.env_var_bonus([clean, dirty]) == 20
    assert blast_radius.env_var_bonus([dirty, clean]) == 20


def test_env_var_bonus_handles_unreadable(tmp_path: Path) -> None:
    """Unreadable / non-existent paths must not crash; they contribute 0."""
    nonexistent = tmp_path / "missing.py"
    assert blast_radius.env_var_bonus([nonexistent]) == 0


# ---------- call_paths_estimate ----------

def test_call_paths_estimate_empty_list(tmp_path: Path) -> None:
    """No paths → 0 (no work)."""
    assert blast_radius.call_paths_estimate(tmp_path, []) == 0


def test_call_paths_estimate_only_irrelevant_extensions(tmp_path: Path) -> None:
    """Paths only have .md / .yaml — no code basenames → 0."""
    a = tmp_path / "a.md"
    a.write_text("# title\n")
    b = tmp_path / "b.yaml"
    b.write_text("key: value\n")
    assert blast_radius.call_paths_estimate(tmp_path, [a, b]) == 0


# ---------- compute ----------

def test_compute_empty_diff_returns_zero(tmp_path: Path) -> None:
    """When there are no changed files, score is 0 and components are zeroed."""
    # tmp_path is not a git repo → changed_files returns [] → score 0.
    result = blast_radius.compute(tmp_path, "HEAD~1")
    assert result["score"] == 0
    assert result["components"]["files"] == 0
    assert result["components"]["privilege"] == 0  # type: ignore[comparison-overlap]


def test_compute_score_is_int_and_clamped() -> None:
    """compute returns score as int; the min(100, ...) clamp is non-negotiable."""
    # We can't easily fabricate a 100+ raw score without a real git repo, but we
    # can assert the clamp contract is in the code path via small synthetic input.
    # This is mostly a documentation test that the contract is wired.
    src = (SKILL / "tools" / "blast_radius.py").read_text()
    assert "min(100" in src, "score clamp removed"
    assert "int(round(" in src, "int(round()) coercion removed"


def test_compute_components_keys_present(tmp_path: Path) -> None:
    """Result schema is stable; downstream rubric reads these keys."""
    result = blast_radius.compute(tmp_path, "HEAD~1")
    assert set(result.keys()) == {"score", "components"}
    expected_subkeys = {"files", "privilege", "call_paths", "env_var_bonus"}
    assert expected_subkeys.issubset(result["components"].keys())


# ---------- CLI main ----------

def test_cli_main_nonexistent_path_returns_2() -> None:
    """Non-directory argument → exit 2 (invocation error)."""
    out = subprocess.run(
        [sys.executable, str(SKILL / "tools" / "blast_radius.py"), "/tmp/does-not-exist-xyz-blast"],
        capture_output=True,
        text=True,
    )
    assert out.returncode == 2, f"expected exit 2, got {out.returncode} (stderr={out.stderr!r})"
    assert "not a directory" in out.stderr


def test_cli_main_emits_json(tmp_path: Path) -> None:
    """When directory has no git diff (or no git), output is valid JSON."""
    out = subprocess.run(
        [sys.executable, str(SKILL / "tools" / "blast_radius.py"), str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0, f"expected exit 0, got {out.returncode} (stderr={out.stderr!r})"
    payload = json.loads(out.stdout)
    assert "score" in payload and "components" in payload


# ---------- runner ----------

def main() -> int:
    failures: list[str] = []
    cases = [
        ("privilege_internal_for_unmatched", test_privilege_internal_for_unmatched, False),
        ("privilege_public_api", test_privilege_public_api, False),
        ("privilege_public_dir", test_privilege_public_dir, False),
        ("privilege_write_effect_db", test_privilege_write_effect_db, False),
        ("privilege_write_effect_migrations", test_privilege_write_effect_migrations, False),
        ("privilege_write_effect_schema", test_privilege_write_effect_schema, False),
        ("privilege_secret_handling_via_path", test_privilege_secret_handling_via_path, False),
        ("privilege_secret_handling_via_filename_password", test_privilege_secret_handling_via_filename_password, False),
        ("privilege_secret_handling_via_filename_secret", test_privilege_secret_handling_via_filename_secret, False),
        ("privilege_secret_handling_via_filename_token", test_privilege_secret_handling_via_filename_token, False),
        ("privilege_secret_handling_via_filename_crypto", test_privilege_secret_handling_via_filename_crypto, False),
        ("privilege_admin_write_effect", test_privilege_admin_write_effect, False),
        ("privilege_styles_internal_css", test_privilege_styles_internal_css, False),
        ("privilege_styles_internal_scss", test_privilege_styles_internal_scss, False),
        ("privilege_styles_dir", test_privilege_styles_dir, False),
        ("privilege_docs_md", test_privilege_docs_md, False),
        ("privilege_docs_dir", test_privilege_docs_dir, False),
        ("privilege_md_extension_anywhere", test_privilege_md_extension_anywhere, False),
        ("privilege_first_match_wins_api_over_admin", test_privilege_first_match_wins_api_over_admin, False),
        ("privilege_secret_keyword_beats_internal", test_privilege_secret_keyword_beats_internal, False),
        ("env_var_bonus_zero_for_clean_file", test_env_var_bonus_zero_for_clean_file, True),
        ("env_var_bonus_python_os_environ", test_env_var_bonus_python_os_environ, True),
        ("env_var_bonus_python_getenv", test_env_var_bonus_python_getenv, True),
        ("env_var_bonus_node_process_env", test_env_var_bonus_node_process_env, True),
        ("env_var_bonus_java_system_getenv", test_env_var_bonus_java_system_getenv, True),
        ("env_var_bonus_php_env_brackets", test_env_var_bonus_php_env_brackets, True),
        ("env_var_bonus_early_exit", test_env_var_bonus_early_exit, True),
        ("env_var_bonus_handles_unreadable", test_env_var_bonus_handles_unreadable, True),
        ("call_paths_estimate_empty_list", test_call_paths_estimate_empty_list, True),
        ("call_paths_estimate_only_irrelevant_extensions", test_call_paths_estimate_only_irrelevant_extensions, True),
        ("compute_empty_diff_returns_zero", test_compute_empty_diff_returns_zero, True),
        ("compute_score_is_int_and_clamped", test_compute_score_is_int_and_clamped, False),
        ("compute_components_keys_present", test_compute_components_keys_present, True),
        ("cli_main_nonexistent_path_returns_2", test_cli_main_nonexistent_path_returns_2, False),
        ("cli_main_emits_json", test_cli_main_emits_json, True),
    ]
    for name, fn, needs_tmp in cases:
        try:
            if needs_tmp:
                with tempfile.TemporaryDirectory() as td:
                    fn(Path(td))
            else:
                fn()
        except AssertionError as e:
            failures.append(f"  FAIL {name}: {e}")
        except Exception as e:  # surface unexpected errors with traceback shape
            failures.append(f"  ERROR {name}: {type(e).__name__}: {e}")
    if failures:
        print(f"test_blast_radius.py: FAIL ({len(failures)}/{len(cases)} cases)")
        for f in failures:
            print(f)
        return 1
    print(f"test_blast_radius.py: PASS ({len(cases)} cases)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
