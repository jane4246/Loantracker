# LoanTrack full-stack demo

This is a test-only loan-progress portal with a Flask backend, browser sessions, customer/manager logins, a seeded test database, and shared status updates.

## Test accounts

| Role | Username | Password/PIN |
| --- | --- | --- |
| Customer | `LT-260912-041` | `2468` |
| Customer | `LT-260911-018` | `1357` |
| Manager | `manager.demo` | `Manager2026!` |

Sign in as the manager, update a case, sign out, and then sign in as the matching customer to see the progress bar change.

## Render deployment

1. Create a separate GitHub repository and upload all files in this folder.
2. In Render, choose **New → Blueprint**, select the repository, and deploy.
3. Open the generated `onrender.com` address.

Render's filesystem can reset on a redeploy or restart. The app automatically recreates its fictional demo data, so that is fine for presentation use. Do not add real customer data.

## Production boundary

This is not a banking or lending system. It has no production authentication, KYC, regulatory integration, audit-security controls, or encrypted bank-data architecture. A real release requires written bank authorization, professional security review, and legal/compliance approval.
