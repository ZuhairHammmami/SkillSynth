# SS-EDS: Business

## Purpose
Document the business model, monetization strategy, market positioning, and operational constraints for SkillSynth. Covers deployment models (self-hosted vs. SaaS), pricing tiers, and revenue drivers.

## Responsibilities
- Define business model (open-core + premium)
- Track operational costs (LLM API, SendGrid, hosting)
- Document licensing (AGPL? Custom?)
- Manage deployment targets (Render, Vercel, Supabase)

## Inputs
- Market analysis
- Infrastructure cost reports
- Competitive pricing data

## Outputs
- Pricing tier definitions
- Cost-per-user estimates
- Deployment cost projections

## Dependencies
- 17-deployment (infrastructure costs)
- 01-product (features determine tiers)
- 14-security (compliance requirements)

## Sequence: User Onboarding to Revenue
```
Sign Up → Free Tier → Usage → Engagement → Upgrade Prompt → Paid Tier
                                          ↓
                                    Feature Gate
                                          ↓
                                Premium Feature Unlock
```

## State Diagram: Subscription Lifecycle
```
[Trial] → [Active] → [Past Due] → [Cancelled] → [Churned]
    ↓          ↓           ↓
[Expired] [Renewed]  [Grace Period]
```

## ERD References
- profiles table ~~(role_id FK → roles)~~ for RBAC-based gating (role_id removed)
- events table for billing analytics

## Rules
- Core learning engine is always free
- Premium features: advanced analytics, LLM-powered explanations, admin reports
- No vendor lock-in — full data export available
- Educational institution discounts available

## Examples
- Free tier: 3 paths, basic analytics, community resources
- Premium: unlimited paths, LLM assistant, priority support

## Edge Cases
- Nonprofit / educational institution pricing
- Enterprise self-hosted vs. cloud SaaS
- Usage-based billing for LLM API calls

## Failure Cases
- LLM API costs exceed revenue (mitigation: hybrid local-first strategy)
- SendGrid delivery failures impact password reset flow
- Supabase overage costs from unoptimized queries

## Recovery Procedures
1. Switch LLM from fallback to local-only mode to cut costs
2. Implement rate limiting on expensive endpoints
3. Review infra costs weekly against budget

## Refactoring Strategy
- Open-core model allows community contributions to core engine
- Premium features are flag-based and testable in dev
- Regular cost audit every sprint
