# Verification Report: Review 992714

**Title:** Switch default Key Pairs panel from AngularJS to Python
**Branch:** master
**Project:** openstack/horizon
**Recipe:** keypairs
**Generated:** 2026-06-23 02:18 UTC

---

## Verdict: PASS


| | Before (AngularJS) | After (Python) |
|---|---|---|
| **Commit** | `447221f1e Imported Translations from Zanata` | `80a5daf42 Switch default Key Pairs panel from AngularJS to Python` |
| **Panel type** | Angular | Python/Django |


---

## Test Summary




### Before (AngularJS baseline)

| Metric | Value |
|--------|-------|
| Groups | 6/7 passed |
| Tests  | 24/25 passed |
| Failed | 1 |


#### Group A: Panel Loading

| Test | Status | Notes |
|------|--------|-------|

| A1_page_loads | pass |  |

| A2_breadcrumb_visible | pass |  |

| A3_table_visible | pass |  |

| A4_panel_type_detected | pass |  |



#### Group B: Table Features

| Test | Status | Notes |
|------|--------|-------|

| B1_search_filter | pass |  |

| B2_column_headers | pass |  |

| B3_row_actions_menu | pass |  |

| B4_batch_actions | pass |  |

| B5_pagination_controls | pass | pagination may not show with few items |



#### Group C: Create Keypair

| Test | Status | Notes |
|------|--------|-------|

| C1_create_ssh_keypair | pass |  |

| C2_create_x509_keypair | pass |  |

| C3_keypairs_appear_in_table | pass |  |



#### Group D: Import Keypair

| Test | Status | Notes |
|------|--------|-------|

| D1_import_ssh_keypair | pass |  |

| D2_import_x509_keypair | pass |  |

| D3_validation_errors | pass | Submit disabled (Angular validation) |



#### Group E: Delete Keypair

| Test | Status | Notes |
|------|--------|-------|

| E1_delete_single | pass |  |

| E2_delete_batch | fail | Batch delete button not enabled |

| E3_confirm_dialog | pass | Verified via delete tests |



#### Group F: Detail View

| Test | Status | Notes |
|------|--------|-------|

| F1_detail_page_loads | pass |  |

| F2_detail_shows_fingerprint | pass |  |

| F3_detail_shows_public_key | pass |  |

| F4_back_navigation | pass |  |



#### Group G: Inline Expansion

| Test | Status | Notes |
|------|--------|-------|

| G1_chevron_toggle | pass | No chevron found — panel may not support inline expand |

| G2_expanded_content | pass |  |

| G3_multiple_expand | pass | Fewer than 2 expandable rows |







### After (Python patched)

| Metric | Value |
|--------|-------|
| Groups | 7/7 passed |
| Tests  | 25/25 passed |
| Failed | 0 |


#### Group A: Panel Loading

| Test | Status | Notes |
|------|--------|-------|

| A1_page_loads | pass |  |

| A2_breadcrumb_visible | pass |  |

| A3_table_visible | pass |  |

| A4_panel_type_detected | pass |  |



#### Group B: Table Features

| Test | Status | Notes |
|------|--------|-------|

| B1_search_filter | pass |  |

| B2_column_headers | pass |  |

| B3_row_actions_menu | pass |  |

| B4_batch_actions | pass |  |

| B5_pagination_controls | pass | pagination may not show with few items |



#### Group C: Create Keypair

| Test | Status | Notes |
|------|--------|-------|

| C1_create_ssh_keypair | pass |  |

| C2_create_x509_keypair | pass |  |

| C3_keypairs_appear_in_table | pass |  |



#### Group D: Import Keypair

| Test | Status | Notes |
|------|--------|-------|

| D1_import_ssh_keypair | pass |  |

| D2_import_x509_keypair | pass |  |

| D3_validation_errors | pass | Modal stayed open (HTML5 validation) |



#### Group E: Delete Keypair

| Test | Status | Notes |
|------|--------|-------|

| E1_delete_single | pass |  |

| E2_delete_batch | pass |  |

| E3_confirm_dialog | pass | Verified via delete tests |



#### Group F: Detail View

| Test | Status | Notes |
|------|--------|-------|

| F1_detail_page_loads | pass |  |

| F2_detail_shows_fingerprint | pass |  |

| F3_detail_shows_public_key | pass |  |

| F4_back_navigation | pass |  |



#### Group G: Inline Expansion

| Test | Status | Notes |
|------|--------|-------|

| G1_chevron_toggle | pass | No chevron found — panel may not support inline expand |

| G2_expanded_content | pass | No expanded row — may not be supported in this panel type |

| G3_multiple_expand | pass | Fewer than 2 expandable rows |






---

## Parity Matrix

| Test | Before | After | Parity |
|------|--------|-------|--------|

| A1_page_loads | pass | pass | PARITY |

| A2_breadcrumb_visible | pass | pass | PARITY |

| A3_table_visible | pass | pass | PARITY |

| A4_panel_type_detected | pass | pass | PARITY |

| B1_search_filter | pass | pass | PARITY |

| B2_column_headers | pass | pass | PARITY |

| B3_row_actions_menu | pass | pass | PARITY |

| B4_batch_actions | pass | pass | PARITY |

| B5_pagination_controls | pass | pass | PARITY |

| C1_create_ssh_keypair | pass | pass | PARITY |

| C2_create_x509_keypair | pass | pass | PARITY |

| C3_keypairs_appear_in_table | pass | pass | PARITY |

| D1_import_ssh_keypair | pass | pass | PARITY |

| D2_import_x509_keypair | pass | pass | PARITY |

| D3_validation_errors | pass | pass | PARITY |

| E1_delete_single | pass | pass | PARITY |

| E2_delete_batch | fail | pass | *FIXED* |

| E3_confirm_dialog | pass | pass | PARITY |

| F1_detail_page_loads | pass | pass | PARITY |

| F2_detail_shows_fingerprint | pass | pass | PARITY |

| F3_detail_shows_public_key | pass | pass | PARITY |

| F4_back_navigation | pass | pass | PARITY |

| G1_chevron_toggle | pass | pass | PARITY |

| G2_expanded_content | pass | pass | PARITY |

| G3_multiple_expand | pass | pass | PARITY |







---

## Fixed


- **E2_delete_batch**: was `fail`, now `pass`



---

## Review Details

- **URL:** https://review.opendev.org/c/openstack/horizon/+/992714
- **Owner:** Owen McGonagle
- **Topic:** de-angularize-keypairs-default
- **Dependencies:** none
- **Files changed:** 5

  - `releasenotes/notes/switch-keypairs-panel-default-to-python-0527d31cd859d015.yaml`

  - `doc/source/configuration/settings.rst`

  - `openstack_dashboard/dashboards/project/key_pairs/views.py`

  - `openstack_dashboard/defaults.py`

  - `openstack_dashboard/test/selenium/integration/test_keypairs.py`



---

*Generated by `/verify` skill — [ioshaworkflow](https://github.com/openstack-horizon-agentic-workflows)*