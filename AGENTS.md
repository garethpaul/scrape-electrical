# AGENTS.md

## Repository purpose

`garethpaul/scrape-electrical` is a public sample, documentation, or utility project. Personal scrape for * electrical with a given URL

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `tests` - tests and fixtures
- `requirements.txt` - Python runtime dependencies
- `plans` - repository source or sample assets

## Development commands

- Install dependencies: `python3 -m pip install -r requirements.txt`
- Full baseline: `make check`
- Combined verification: `make verify`
- Lint/static checks: `make lint`
- Tests: `make test`
- Build: `make build`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: Python (1).
- Prefer dependency-free tests or stdlib checks when legacy packages are unavailable.

## Testing guidance

- Test-related files detected: `tests/`, `tests/test_scrape.py`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- Live PostgreSQL runs require operator-provided database connection fields. Keep credentials in the shell or a local secret manager; do not commit them.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-scrape-electrical-baseline.md` for the canonical scraper/database safety baseline.
- See `docs/plans/2026-06-08-network-timeout.md` for the network timeout guard.
- Scraper timeouts must be finite positive numbers before network setup.
- See `docs/plans/2026-06-08-parser-link-guard.md` for incomplete product-link handling.
- Hosted checks must run the complete offline Python 2 suite in the reviewed
  digest-pinned container with credential-free checkout, read-only
  permissions, and no live dependency installation.
- Run `make contract-test` after workflow changes. Duplicate, relocated, or
  contradictory credential settings and other policy drift must fail closed.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
