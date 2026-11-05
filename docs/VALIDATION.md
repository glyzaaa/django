# Validation — dark design edition

## Application and activity checks

| Suite | Student starter | Completed instructor algorithms |
| --- | --- | --- |
| Django application | 57 passed | 57 passed |
| Queue goal | 3 passed, 7 intentional failures | 10 passed |
| Singly linked-list goal | 10 passed, 7 intentional failures | 17 passed |
| Combined | 70 passed, 14 intentional goal failures | 84 passed |

The student algorithm files are byte-identical to the attached fullstack starter.
The two exercise goals remain intentionally unfinished. The redesign changes
presentation, shared templates, and read-only dashboard chart calculations.

## Design and browser verification

- Desktop: actual dashboard charts, request creation, detail actions, table,
  Kanban view, service queue, and matching sign-in screen inspected in Chrome.
- Phone: dashboard/workflow inspected at 375px usable width; request cards/queue
  inspected at 345px usable width. Each page's body scroll width equals its
  usable width; no horizontal page overflow was found.
- Request creation and enqueue were exercised through actual HTML forms.
- Workflow insertion was exercised through the phone form, saved by Django,
  and visibly rendered after the POST/redirect.
- The reference's navy panels, purple/cyan accents, active navigation marker,
  compact KPI/chart panels and bordered table/board styles were used throughout.
- Bundled Inter/font license are local. No font CDN is required.
- Browser checks use disposable fixture authentication/data in an excluded QA
  adapter. The downloadable project uses its original Django authentication.
- Public matching-kit previews were accessible. Exact selected Figma node
  5401:1157 could not be verified; see DESIGN_REFERENCE.md.

## Project integrity

Django system checks pass; migration drift check reports no changes. Existing
account/database migrations, student methods, role guards and persistence remain
in place. No additional Python dependency or database migration is needed.
Production security/static checks include the new local font and CSS assets.
Fresh archive checks exclude environments, generated databases, local keys,
completed answers, screenshots and all preview adapters.

The original fullstack release's portable setup was verified on Python 3.12.14
with Django 5.2.18. Setup/launch scripts are unchanged in this design update.
Windows .bat execution, live Docker/PostgreSQL infrastructure and external SMTP
were not available here. No new live deployment, load certification, formal
accessibility certification or independent security audit is claimed.
