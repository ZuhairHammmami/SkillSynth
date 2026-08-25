# SS-EDS: Glossary

## Purpose
Provide a comprehensive glossary of terms used across SkillSynth documentation, codebase, and domain language. Includes both technical terms and synth-metaphor replacements.

## Responsibilities
- Maintain consistent terminology across the project
- Document synth-metaphor term replacements
- Define domain-specific terminology
- Provide cross-references to relevant documentation

## Inputs
- Codebase terminology
- Design system term replacements
- Domain language from learning science

## Outputs
- Alphabetical glossary
- Metaphor term mapping

## Dependencies
- 05-domain (domain language)
- 20-ui-system (design term replacements)

## Glossary

### A
- **Achievements**: ~~Milestones awarded for completing N steps (1/10/50/100) or reaching N level~~ **REMOVED**
- **ADRs**: Architectural Decision Records — documentation of significant architecture decisions
- **AEIS**: Adaptive Education Information Schema — Supabase schema for mastery tracking
- **Amplifier Rack**: Manager Studio component showing group/department learner overview
- **Assessment**: Quiz or test that evaluates learner skill proficiency

### B
- **Brass (#D4A843)**: Primary accent color for active states, cables, and highlights
- **Bounded Context**: Domain-driven design concept — distinct area of the domain with its own model

### C
- **Cable**: SVG Bézier curve connecting module jacks, representing connections
- **Chamfer**: 2px diagonal cut on module corners via clip-path
- **Command Rail**: Top navigation bar with logo, section knobs, and user module

### D
- **DAG**: Directed Acyclic Graph — prerequisite structure for learning path generation
- **Domain Event**: Significant occurrence within the domain (step_completed, assessment_completed)

### E
- **Events Table**: Database table logging all system events for audit and learning analytics
- **External Resource**: Learning material (video, article, book) linked to path steps

### F-K
- **Gamification**: ~~XP, levels, achievements,~~ and streaks for learner motivation — **XP/achievements removed, streaks retained**
- **Jack**: Circular connection point on modules (input/output)
- **Junction Tables**: skill_categories, skill_prerequisites, job_role_skills, path_skills
- **Kahn's Algorithm**: Topological sort algorithm for prerequisite DAG resolution

### L-P
- **LED**: 8px notification indicator on modules with color/animation states
- **Level**: ~~Learner progression level (each level = level * 100 XP total)~~ **REMOVED**
- **Module**: Self-contained UI component (synth metaphor) — primary building block
- **N+1 Query**: Anti-pattern where related data is fetched in a loop (10 instances fixed in Phase 9)
- **Patch Bay**: The main workspace area where modules are placed and connected

### Q-Z
- **RBAC**: Role-Based Access Control — 6 roles with granular permissions
- **RTL**: Right-to-Left layout — Arabic-first design
- **SSE**: Server-Sent Events — real-time event streaming
- **Skill Profile**: JSON object on Profile storing proficiency levels per skill
- **Streak**: Consecutive days of learning activity
- **Teal (#3D5A5C)**: Secondary accent color for learning paths and calm indicators
- **XP**: ~~Experience Points — earned by completing steps (+10) or deducted by undo (-10)~~ **REMOVED**

## Metaphor Term Replacements
| Standard Term | Synth Term |
|---------------|------------|
| Login | Signal Tuning |
| Button | Knob / Jack |
| Progress bar | VU Meter |
| Dashboard | Workspace / Patch Bay |
| Sidebar | Command Rail |
| Form | Control Panel / Groove |
| Error | System Noise |
| Success | Signal Locked |

## ERD References
- Glossary terms map to database entities

## Rules
1. Terms must have a single, unambiguous definition
2. Cross-references to related docs must be maintained
3. Synth metaphor replacements must be used in user-facing text
4. Technical terms (SSE, RBAC, DAG) defined in plain language

## Examples
- "Login" → always displayed as "Signal Tuning" in UI, but code uses "login"
- "Skill profile" → stored as JSON, displayed as proficiency levels

## Edge Cases
- Term used differently in code vs. UI → note both definitions
- New term introduced → add to glossary before use
- Metaphor term confusion → clarify with examples

## Failure Cases
- Missing glossary entry → add when discovered
- Contradictory definitions → resolve and update
- Outdated metaphor mapping → review with design team

## Recovery Procedures
1. Search codebase for term usage patterns
2. Align definition with actual usage
3. Update all documentation referencing the term

## Refactoring Strategy
- Generate glossary from code annotations
- Link glossary terms to documentation sections
- Add glossary search functionality to docs website
