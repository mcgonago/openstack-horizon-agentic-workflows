# Launchpad and OpenStack

## Launchpad Bug Lifecycle

Launchpad bug statuses:
- New: freshly filed, no triage
- Confirmed: bug reproduced or acknowledged
- Triaged: importance set, ready for work
- In Progress: someone is working on it
- Fix Committed: fix merged to source (not released yet)
- Fix Released: included in a release
- Invalid: not a bug
- Won't Fix: acknowledged but will not be fixed
- Opinion: design disagreement, not a defect
- Expired: no activity, auto-closed

## Importance Levels

- Critical: system unusable, data loss, security vulnerability
- High: major feature broken, no workaround
- Medium: feature broken with workaround
- Low: minor issue, cosmetic
- Wishlist: enhancement request
- Undecided: not yet triaged

## OpenStack-Specific Patterns

- hudson-openstack bot posts "Fix merged" comments with Gerrit review links
- Bugs often affect multiple projects (e.g., a library bug affects services)
- Cross-project bugs track status independently per project
- Gate-breaking bugs get fast-tracked via emergency procedures
- oslo.* libraries are shared infrastructure -- changes can break many services

## Launchpad REST API

- Base: https://api.launchpad.net/devel/bugs/{id}
- Public bugs require no authentication
- Bug tasks (per-project status): /bug_tasks endpoint
- Messages (comments): /messages endpoint
- Activity log: /activity endpoint
- Usernames are parsed from owner_link URLs (last segment after ~)

## Horizon-Specific Context

- Horizon uses oslo.policy for RBAC policy enforcement
- Policy credentials include domain_id, project_id, user_id
- openstack_auth/policy.py is the policy enforcement layer
- Changes to oslo.policy scope rules directly affect which UI elements appear
- Horizon's openstack_auth code is 9+ years old -- predates many modern patterns
