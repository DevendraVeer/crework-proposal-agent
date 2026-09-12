Subject: Proposal for Vantage Networks — Support Ticket Triage System

## Overview
Vantage Networks' senior engineers currently spend a meaningful chunk of
each day manually reading, prioritizing and routing incoming support
tickets before they can get back to actual engineering work. This proposal
covers an AI triage layer that reads every incoming ticket, determines
severity and the right specialization, routes it automatically, and
escalates anything security-critical immediately rather than letting it
sit in a general queue.

## Scope of Work
- Ingest tickets from the existing helpdesk tool via its API.
- Build a classification step that reads ticket content and assigns
  severity, category and the correct technician queue.
- Add an immediate escalation path: anything flagged as security-critical
  pings the on-call engineer directly, bypassing the normal queue.
- Provide a weekly summary of ticket volume and triage accuracy so the
  team can spot-check the system.

## Deliverables
- Live triage pipeline integrated with the existing helpdesk tool.
- Real-time security escalation alerting.
- Weekly triage accuracy report.

## Timeline
3 weeks: week one for classification accuracy, week two for the
escalation path and integration testing, week three running in shadow
mode alongside manual triage before full cutover.

## Investment
$4,200 for the build, reflecting the security-critical escalation logic
and integration work. $400/month for ongoing monitoring and
reclassification tuning.

## Next Steps
We'll need read access to a sample of the last 90 days of tickets to tune
classification accuracy before going live.
