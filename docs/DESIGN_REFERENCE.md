# Dark dashboard design

## Visual reference

Requested Figma file:
https://www.figma.com/design/aVRzocZJappzaIylWB54gy/Free-Dark-Admin-Dashboards--Community-?node-id=5401-1157

Public community kit:
https://www.figma.com/community/file/1325597018063319916/free-dark-admin-dashboards

The supplied reference is the Free Dark Admin Dashboards community kit, with
Dashdark X dashboard, analytics, Kanban, messages and user-table examples.
The previews identify Dashdark X / BRIX Templates. The reference's publicly
listed screenshots were inspected here:
https://soscut.com/free_source/8240

Figma installation was confirmed during this task. Its design-reading tools
were not exposed in the active runtime, and the shared file's browser view
returned HTTP 403. This implementation therefore adapts the matching kit's
public previews; exact geometry/layers of node 5401:1157 were not verified.

## Applied design system

| Token | Value / treatment |
| --- | --- |
| Canvas / navigation | #081028 |
| Card panels | #0D1738 |
| Secondary panel | #101D42 |
| Borders | #263252 |
| Primary text | #F5F6FF |
| Secondary text | #A9B2D5 |
| Purple accent / activity series | #CB3CFF |
| Cyan accent / completion series | #00C2FF |
| Primary actions | Purple gradient with readable white labels |
| Typography | Local Inter variable font; system fallback |
| Navigation | Persistent left sidebar, search, purple active marker, account footer |
| Layout | Four KPI cards, large activity chart, compact status/rate panels, table and team activity |
| Small screens | Collapsible navigation, request cards, stacked panels and readable forms |

The Flowdesk brand, actual application links, roles and request terminology are
retained. Revenue, sample subscriptions, invented percentages, fictional users
and unrelated kit features are not introduced into the product.

Every metric uses the current workspace's database records. Request activity
compares created/completed requests over seven local dates. A workspace without
requests displays zero/empty states. Status counts and the completion gauge
represent current non-archived requests. No reference screenshot is embedded as
a page background or product image.

## Source locations

- `frontend/static/app.css`: centralized tokens, component styles and breakpoints.
- `frontend/static/fonts/`: locally bundled Inter and its license.
- `frontend/templates/base.html`: navigation, search and account shell.
- `frontend/templates/dashboard.html`: actual SVG charts and live summary panels.
- `backend/workspace/presentation.py`: view-only chart coordinates from real data.
- `backend/workspace/views.py`: tenant-scoped dashboard queries.
- Other existing templates inherit the same theme without changing their routes.

Existing Django forms, ORM models, permissions, CSRF protection, persistence and
student algorithm integration remain in place. No model migration or extra
Python dependency is needed. The reference design is a visual guide; its brand,
logo, model photos and screenshot assets are not redistributed as Flowdesk UI.

Inter source: https://github.com/rsms/inter
Font license: `frontend/static/fonts/LICENSE.txt` (SIL Open Font License).
