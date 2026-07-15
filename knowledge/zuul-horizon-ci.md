# Horizon CI Knowledge Base — Zuul Job Analysis

Domain knowledge for classifying Zuul CI failures in the OpenStack Horizon project.
Used by the `/zuul-job` skill and the `zuul-analyst` agent persona.

---

## Section 1: Horizon CI Job Taxonomy

### Unit Test Jobs (tox-based)

| Job | What It Tests | Voting | Duration | Tox Env |
|-----|--------------|--------|----------|---------|
| `openstack-tox-pep8` | Linting (flake8, hacking, eslint, bandit) | YES | ~5 min | `pep8` |
| `openstack-tox-py311` | Python 3.11 unit tests | YES | ~15 min | `py311` |
| `openstack-tox-py313` | Python 3.13 unit tests | YES | ~20 min | `py313` |
| `openstack-tox-py314` | Python 3.14 unit tests | **NO** | ~25 min | `py314` |
| `horizon-tox-python3-django42` | Django 4.2 compatibility | YES | ~20 min | `py3-dj42` |
| `horizon-tox-python3-django52` | Django 5.2 compatibility | YES | ~20 min | `py3-dj52` |

### JavaScript Jobs

| Job | What It Tests | Voting | Duration |
|-----|--------------|--------|----------|
| `horizon-nodejs20-run-lint` | ESLint + stylelint | YES | ~5 min |
| `horizon-nodejs20-run-test` | Karma JS unit tests | YES | ~8 min |

### Integration Jobs (DevStack-based)

| Job | What It Tests | Voting | Duration |
|-----|--------------|--------|----------|
| `horizon-selenium-headless` | Selenium tests (headless Firefox) | YES | ~9 min |
| `horizon-integration-pytest` | Full integration tests against DevStack | YES | ~80 min |
| `horizon-ui-pytest` | UI-specific Selenium tests | YES | ~25 min |
| `horizon-dsvm-tempest-plugin` | Tempest plugin tests against DevStack | YES | ~30 min |
| `horizon-tempest-plugin-ipv6` | IPv6 tempest plugin tests | YES | ~18 min |

### Security / Docs Jobs

| Job | What It Tests | Voting | Duration |
|-----|--------------|--------|----------|
| `horizon-tox-bandit-baseline` | Security scan (bandit) | YES | ~4 min |
| `build-openstack-releasenotes` | Reno release notes build | YES | ~10 min |
| `openstack-tox-docs` | Documentation build | YES | ~8 min |

### Cross-Project Jobs (all NON-voting)

| Job | What It Tests | Duration |
|-----|--------------|----------|
| `horizon-cross-manila-ui-python` | Manila UI plugin compatibility | ~5 min |
| `horizon-cross-heat-dashboard-python` | Heat dashboard compatibility | ~5 min |
| `horizon-cross-ironic-ui-npm` | Ironic UI npm build | ~5 min |
| `horizon-cross-designate-dashboard-python` | Designate dashboard compat | ~5 min |
| `horizon-cross-octavia-dashboard-python` | Octavia dashboard compat | ~5 min |
| `horizon-cross-magnum-ui-python` | Magnum UI compatibility | ~5 min |

---

## Section 2: Known Flake Patterns

### Flake 1: Selenium TimeoutException

- **Error signature:** `selenium.common.exceptions.TimeoutException`
- **Jobs affected:** `horizon-integration-pytest`, `horizon-ui-pytest`, `horizon-selenium-headless`
- **Classification:** INFRA-FLAKE (if our patch did NOT change the template/view the test exercises)
- **Classification:** CODE-REGRESSION (if our patch DID change the template/view)
- **Decision rule:** Check if the element/page the timeout occurred on is in a file we modified. If not → INFRA-FLAKE.
- **Frequency:** ~15% of integration test runs
- **Evidence:** Seen in osprh_16421 patchsets 8, 9 (recheck resolved); 992714 PS1

### Flake 2: RETRY_LIMIT

- **Error signature:** `RETRY_LIMIT` in Zuul result
- **Jobs affected:** `horizon-ui-pytest` (most common), any job
- **Classification:** INFRA-FLAKE (Zuul environment instability, not code)
- **Frequency:** ~5% of runs
- **Evidence:** Seen in ideangularize review 992675

### Flake 3: Python 3.14 super() AttributeError

- **Error signature:** `AttributeError: 'super' object has no attribute 'dicts'`
- **Jobs affected:** `openstack-tox-py314` (non-voting)
- **Classification:** SKIP (Python 3.14 compatibility issue, non-voting job)
- **Frequency:** ~80% of py314 runs (known upstream issue)
- **Evidence:** Seen in osprh_26399 patch 6
- **Action:** Ignore — non-voting, upstream Python issue

### Flake 4: Mirror Connection Refused

- **Error signature:** `Connection refused` with `mirror.*.raxflex.opendev.org`
- **Jobs affected:** Any job (pre-run phase)
- **Classification:** INFRA-FLAKE (mirror connectivity, transient)
- **Frequency:** ~10% of runs
- **Decision rule:** Check if `failed: 0` in the play recap — if so, the mirror issue was recovered.
- **Evidence:** Intermittent across many reviews

### Flake 5: NoSuchElementException on Unchanged Panel

- **Error signature:** `selenium.common.exceptions.NoSuchElementException`
- **Jobs affected:** `horizon-integration-pytest`, `horizon-selenium-headless`
- **Classification:** CODE-REGRESSION (if our patch changed the panel/template the test exercises)
- **Classification:** INFRA-FLAKE (if our patch did NOT change the relevant panel/template)
- **Decision rule:** Check if the XPath/CSS selector in the error points to an element in a template we modified. If we changed `key_pairs/` templates and the test fails on a key pair element → CODE-REGRESSION. If the test fails on the `images/` panel and we only changed `key_pairs/` → INFRA-FLAKE.

### Flake 6: Merge Conflict

- **Error signature:** `MERGER_FAILURE` in Zuul result
- **Jobs affected:** All jobs (pre-run)
- **Classification:** UPSTREAM-DEP (conflicting change merged to master)
- **Action:** Rebase onto latest master: `git review -d <change> && git rebase master && git review`

---

## Section 3: Error Pattern → Category Mapping

Use this table as a lookup BEFORE applying judgment. If the error matches
a pattern here, use the listed category. If ambiguous, use the decision
rules from Section 2.

| Error Pattern | Category | Notes |
|--------------|----------|-------|
| `NoReverseMatch: Reverse for '...' not found` | CODE-REGRESSION | URL pattern missing from urls.py |
| `TemplateDoesNotExist: ...` | CODE-REGRESSION | Template path wrong in view |
| `ImportError: cannot import name '...'` | CODE-REGRESSION | Import path or symbol wrong |
| `SyntaxError` | CODE-REGRESSION | Python syntax error in our code |
| `AssertionError` (in our test files) | CODE-REGRESSION | Test assertion failure |
| `E501 line too long` (in our files) | CODE-REGRESSION | Linting: line too long |
| `W291 trailing whitespace` | CODE-REGRESSION | Linting: trailing whitespace |
| `W293 whitespace before ':'` | CODE-REGRESSION | Linting: whitespace issue |
| `R1725 super-with-arguments` | CODE-REGRESSION | Use `super()` not `super(Cls, self)` |
| `W0246 useless-parent-delegation` | CODE-REGRESSION | Remove redundant `__init__` |
| `H404/H405` (hacking) | CODE-REGRESSION | Docstring format issue |
| `NoSuchElementException` (our panel changed) | CODE-REGRESSION | Selenium can't find element we changed |
| `NoSuchElementException` (other panel) | INFRA-FLAKE | Selenium flake on unchanged code |
| `TimeoutException` (Selenium) | INFRA-FLAKE | Selenium timeout (usually transient) |
| `RETRY_LIMIT` | INFRA-FLAKE | Zuul retry exhaustion |
| `Connection refused` (mirror) | INFRA-FLAKE | Mirror connectivity |
| `UNREACHABLE` (Ansible) | INFRA-FLAKE | Node connectivity |
| `pip install` failure (transient) | INFRA-FLAKE | Package mirror issue |
| `tox: command not found` | INFRA-FLAKE | Tox installation issue |
| `AttributeError: 'super' object...dicts` | SKIP | Python 3.14 issue (non-voting) |
| `MERGER_FAILURE` | UPSTREAM-DEP | Merge conflict |
| `TemplateSyntaxError` | CODE-REGRESSION | Django template syntax error |

---

## Section 4: Triage Decision Tree

```
START
  |
  v
Are there any VOTING failures?
  |
  +-- NO --> VERDICT: PASS
  |          All jobs passed. No action needed.
  |
  +-- YES --> Classify each voting failure using Section 3
                |
                v
              All classified as INFRA-FLAKE?
                |
                +-- YES --> How many rechecks on this patchset?
                |             |
                |             +-- < 2 --> VERDICT: RECHECK
                |             |          Post "recheck" on Gerrit.
                |             |
                |             +-- >= 2 --> VERDICT: ESCALATE
                |                          Report to infra team.
                |
                +-- NO --> Any CODE-REGRESSION?
                            |
                            +-- YES --> VERDICT: FIX
                            |           Reproduce locally, fix code,
                            |           push new patchset.
                            |
                            +-- NO --> Only UPSTREAM-DEP?
                                        |
                                        +-- YES --> VERDICT: REBASE
                                        |           Rebase on master,
                                        |           repush.
                                        |
                                        +-- NO --> VERDICT: INVESTIGATE
                                                   Mixed or unknown
                                                   failures. Manual
                                                   review needed.
```

---

## Section 5: Common Fix Recipes

### FIX: NoReverseMatch

**Problem:** URL pattern referenced in template but not registered in urls.py.
**Fix:**
1. Find the URL name in the error message
2. Check `urls.py` for the panel — add the missing pattern
3. Verify: `grep -r "reverse(" <panel>/` to find all usages
**Local test:** `tox -e py313 -- <test_file> -v`

### FIX: TemplateDoesNotExist

**Problem:** `template_name` in view doesn't match actual file path.
**Fix:**
1. Check the view's `template_name` attribute
2. Verify the template file exists at that path under `templates/`
3. Fix the path or move the template
**Local test:** `tox -e py313 -- <test_file> -v`

### FIX: NoSuchElementException (Selenium)

**Problem:** Selenium test looking for element that changed or moved.
**Fix:**
1. Find the XPath/CSS selector in the test
2. Check the template that renders the element
3. Update the selector to match the new HTML structure
**Local test:** `tox -e selenium-headless -- <test_file> -v`

### FIX: Linting Errors (E501, W291, R1725, etc.)

**Problem:** Code style violations caught by flake8/pylint.
**Fix:**
1. Read the error table from the report
2. Fix each violation in the listed file:line
3. Run pep8 locally to verify
**Local test:** `tox -e pep8`

### FIX: ImportError

**Problem:** Module or symbol not found at the import path.
**Fix:**
1. Check the import path in the error
2. Verify the module exists and the symbol is defined
3. Fix the import path or add the missing definition
**Local test:** `tox -e py313 -- <test_file> -v`

---

## Section 6: Recheck Policy

### When to Recheck

- All voting failures are classified as INFRA-FLAKE
- Fewer than 2 previous rechecks for this patchset
- No CODE-REGRESSION failures present

### When NOT to Recheck

- Any CODE-REGRESSION failure exists (fix code first)
- Already rechecked 2+ times (escalate to infra)
- MERGER_FAILURE present (rebase instead of recheck)

### How to Recheck

Post a comment on the Gerrit review with just the word: `recheck`

This triggers a new Zuul check pipeline run.

### Maximum Rechecks

- **2** — If a failure persists after 2 rechecks, escalate to
  openstack-infra or investigate more deeply.

### Recheck Interval

- Wait for the full buildset to complete before rechecking.
- Do not recheck while builds are still running.
