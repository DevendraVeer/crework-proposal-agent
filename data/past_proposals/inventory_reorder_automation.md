Subject: Proposal for Marlow Home Co. — Multi-Channel Inventory Monitoring

## Overview
Marlow Home Co. sells across their own site, Amazon and two marketplaces,
with stock data scattered across three separate systems and reorder
decisions made manually from spreadsheets on a weekly cycle. This has led
to preventable stockouts on best-selling products. This proposal covers a
system that pulls stock and sell-through data from all channels in one
place and flags anything approaching its reorder point early enough to
act — without auto-placing orders, keeping a human in the loop on
purchasing decisions.

## Scope of Work
- Connect Shopify, Amazon Seller Central and the warehouse system into a
  single stock-visibility layer.
- Calculate sell-through rate per SKU per channel and compare against
  reorder thresholds.
- Send an early warning (not an automatic order) when any SKU is
  projected to hit its reorder point within a configurable window.
- Build a simple weekly summary of at-risk SKUs across all channels.

## Deliverables
- Unified stock-and-sell-through view across all three channels.
- Automated early-warning alerts for at-risk SKUs.
- Weekly at-risk-inventory summary.

## Timeline
2.5 weeks: first week connecting and reconciling the three data sources,
remainder spent tuning reorder thresholds against real historical sales
data before go-live.

## Investment
$3,000 flat for the build. $250/month for ongoing monitoring across all
three channels as new SKUs are added.

## Next Steps
We'll need read-only access to Shopify, Amazon Seller Central and your
warehouse system's export to begin reconciling stock data.
