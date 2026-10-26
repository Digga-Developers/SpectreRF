## What this does

<!-- A sentence or two is plenty. Why this change, and anything the reviewer should know. -->

Closes #

## How to test

<!-- The quickest way for a reviewer to see it work, e.g.
     docker compose up -d
     python -m src.main --pcap tests/fixtures/sample.pcap --speed 0
     then open the SOC Overview dashboard -->

## Screenshots

<!-- Dashboard or output changes? Drop a screenshot here. Otherwise delete this section. -->

## Heads-up for the team

<!-- Tick anything that applies and delete the rest. Leave it empty if nothing applies. -->

- [ ] Changes the data contract (`FrameEvent` fields or table columns), so all three of us need to approve
- [ ] Changes `init.sql`: run `docker compose down -v` before testing
- [ ] Adds a new env var (also added to `.env.example`)
- [ ] Adds a new dependency (also added to `requirements.txt`)

## Notes for the reviewer

<!-- Optional. Anything you're unsure about, a shortcut you took, or a follow-up ticket you opened.
     Reviewers: mark comments as "blocking" or "nit". Nits never hold up a merge. -->

