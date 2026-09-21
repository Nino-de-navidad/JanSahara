# JanSahara Frontend — Redesigned

A refreshed, responsive UI for the JanSahara government-scheme discovery platform.

## Included
- Landing page
- Register / Login
- Dashboard
- Profile
- Recommendations
- Eligibility
- Scheme Explorer
- AI Chatbot
- Consistent JanSahara logo / favicon
- Responsive navigation and cards
- Shared visual design system

## Backend compatibility
The existing frontend API calls and local development API base (`http://localhost:5000`) are preserved. No Backend files are included or modified.

The Google Form profile flow is preserved, including the pre-filled `JanSahara User ID` field using `entry.952470711` on the dashboard.

## Run locally
1. Start the Flask backend from the `Backend` folder.
2. From this folder run:

```bash
python -m http.server 5500
```

3. Open `http://localhost:5500`.

Before public deployment, replace the frontend API base URLs with the deployed HTTPS backend URL.
