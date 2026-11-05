# Frontend

`templates/` contains actual Django Templates: base navigation, dashboard,
request list/board/details/forms, queue, workflow, reports, activity, archive,
settings, lab guide and account/team screens.

`static/app.css` defines the product UI, responsive phone request cards, phone
navigation and desktop layouts. `static/app.js` supplies progressive interaction
only; Django handles persistence, authentication, validation and permissions.
All assets are local. No Node build, CDN, JavaScript frontend framework, or
separate frontend process is required.

Templates run through Django. Do not double-click an HTML template as a file.
