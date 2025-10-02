# Club Corra Feature Planning Workflow - SDD Enhanced

## Spec-Driven Development Integration

This enhanced workflow integrates Spec-Driven Development (SDD) using GitHub's spec-kit with Cursor AI and Gemini CLI. All feature planning follows a specification-first approach with streamlined validation.

## Pre-Planning Assessment

### 1. Specification Status Check
Before feature planning, assess the current state:

1. **Check Existing Specifications**
   ```
   @cursor: Check specification for [feature] in spec-kit/specifications/
   ```

2. **Quick Implementation Assessment**
   ```
   @cursor: Assess current implementation status for [feature]
   ```

3. **Update Specs Only If Needed**
   ```
   @cursor: Update [feature] specification if significant gaps exist
   ```

### 2. Specification Files Reference
- **Core Features**: `spec-kit/specifications/club-corra-core.spec.yaml`
- **Mobile Features**: `spec-kit/specifications/mobile-app.spec.yaml` 
- **Admin Features**: `spec-kit/specifications/admin-portal.spec.yaml`
- **API Features**: `spec-kit/specifications/api-backend.spec.yaml`
- **Website Features**: `spec-kit/specifications/website.spec.yaml`

## Enhanced Planning Process

### 1. Specification-First Approach
When the user provides a feature description:

1. **Search for Existing Specification**
   - Check all specification files for related features
   - Identify gaps between spec and requested feature
   - Update or create specification as needed

2. **Validate Business Requirements**
   - Ensure specification captures all user scenarios
   - Verify acceptance criteria are clear
   - Check for cross-platform consistency requirements

3. **Single Validation Check (Optional)**
   ```bash
   # Only run if specification is complex or new:
   @cursor: Validate [feature] specification using Gemini CLI
   # Executes: ./scripts/sdd/validate-spec.sh [feature]
   ```

### 2. Technical Plan Creation
After specification assessment:

1. **Specification Mapping**
   - Map each specification scenario to technical implementation
   - Identify all affected components across the monorepo
   - Plan for cross-platform consistency

2. **Implementation Research**
   - Analyze current codebase for existing patterns
   - Identify reusable components and services
   - Check for potential conflicts or dependencies

3. **Strategic Checkpoints**
   - Define key validation points during implementation
   - Plan for spec synchronization at major milestones
   - Include testing requirements for each scenario

### 3. Task and Phase Division Methodology

Based on current implementation patterns, features should be divided into logical phases:

#### Phase Division Strategy
1. **Foundation Phase**: Core data structures, entities, migrations
2. **Backend Phase**: API endpoints, services, business logic
3. **Frontend Phase**: UI components, screens, user interactions
4. **Integration Phase**: Cross-platform consistency, testing, deployment

#### Task Breakdown Principles
- **Single Responsibility**: Each task should have one clear objective
- **Dependency Management**: Tasks should be ordered by dependencies
- **Platform Separation**: Separate tasks for web, mobile, and API
- **Incremental Delivery**: Each phase should deliver working functionality

#### Current Implementation Patterns
Based on existing plans, use these patterns:

**Data Layer First** (Phase 1):
- Database schema changes and migrations
- Entity updates and shared types
- Zod schema modifications

**Backend Implementation** (Phase 2):
- Service layer development
- Controller endpoints
- Business logic implementation
- Validation and error handling

**Frontend Development** (Phase 3):
- UI component creation
- Screen/page implementation
- User interaction flows
- API integration

**Integration & Polish** (Phase 4):
- Cross-platform testing
- Performance optimization
- Documentation updates
- Deployment preparation

### 4. Enhanced Plan Structure

```markdown
# [Feature Name] Technical Plan

## Specification Status
- **Specification File**: `spec-kit/specifications/[spec-file].spec.yaml`
- **Last Updated**: [Date]
- **Validation Status**: [Passed/Needs Update]
- **Implementation Scope**: [New Feature/Enhancement/Refactor]

## Specification Coverage
### Scenarios to Implement
1. [Scenario Name] - [Implementation approach]
2. [Scenario Name] - [Implementation approach]

### Current Implementation Gaps
- [Gap 1]: [How to address]
- [Gap 2]: [How to address]

## Implementation Phases

### Phase 1: Foundation [Duration: X days]
**Objective**: Set up core data structures and shared components

**Tasks**:
1. [Task 1]: [Description] - [Files to create/modify]
2. [Task 2]: [Description] - [Files to create/modify]

**Deliverables**:
- [Deliverable 1]
- [Deliverable 2]

### Phase 2: Backend Development [Duration: X days]
**Objective**: Implement API endpoints and business logic

**Tasks**:
1. [Task 1]: [Description] - [Files to create/modify]
2. [Task 2]: [Description] - [Files to create/modify]

**Deliverables**:
- [Deliverable 1]
- [Deliverable 2]

### Phase 3: Frontend Implementation [Duration: X days]
**Objective**: Create user interfaces and interactions

**Tasks**:
1. [Task 1]: [Description] - [Files to create/modify]
2. [Task 2]: [Description] - [Files to create/modify]

**Deliverables**:
- [Deliverable 1]
- [Deliverable 2]

### Phase 4: Integration & Testing [Duration: X days]
**Objective**: Ensure cross-platform consistency and quality

**Tasks**:
1. [Task 1]: [Description] - [Files to create/modify]
2. [Task 2]: [Description] - [Files to create/modify]

**Deliverables**:
- [Deliverable 1]
- [Deliverable 2]

## Validation Checkpoints
1. **Phase 1 Complete**: Data layer validation
2. **Phase 2 Complete**: API functionality validation
3. **Phase 3 Complete**: UI/UX validation
4. **Phase 4 Complete**: Full integration validation

## Specification Update Requirements
- [List any spec updates needed during/after implementation]
```

### 5. SDD Workflow Integration

Each plan MUST include streamlined SDD commands:

```markdown
## SDD Workflow Commands

### Pre-Implementation
```bash
# Only run if specification is complex or new:
./scripts/sdd/validate-spec.sh [feature]

# Check implementation drift (if working on existing feature):
./scripts/sdd/check-drift.sh [feature]
```

### During Implementation
```
@cursor: Validate [feature] implementation against specification at phase checkpoints
@cursor: Update [feature] specification if requirements change
```

### Post-Implementation
```bash
# Final validation (only if significant changes made):
./scripts/sdd/validate-spec.sh [feature]

# Update documentation
@cursor: Update [feature] documentation with spec references
```
```

### 5. Cross-Reference Requirements

All plans must maintain these references:
- **Specification Scenarios**: Link each technical component to spec scenarios
- **Validation Points**: Define when to check spec compliance
- **Update Triggers**: Identify when specs need updating
- **Test Coverage**: Map tests to specification scenarios

## Quality Guidelines

### Specification Validation
1. Assess existing specifications before planning (validation only if complex)
2. Update outdated specs BEFORE creating technical plans
3. Ensure 100% scenario coverage in implementation plan
4. Include strategic spec validation commands in the plan

### Clarification Process
If requirements are unclear:
1. First check if specification provides clarity
2. Ask up to 5 clarifying questions if needed
3. Update specification with clarifications
4. Incorporate answers into both spec and plan

### Continuous Sync
- Plans must include spec update triggers at phase checkpoints
- Implementation must maintain spec alignment through phases
- Documentation must reference specifications

## Output Format

### File Structure
```
docs/features/NNNN_[FEATURE]_PLAN.md
```
Where NNNN is the next available number (starting with 0001).

### Required Sections
1. Specification Status
2. Specification Coverage  
3. Technical Implementation
4. Validation Checkpoints
5. SDD Workflow Commands
6. Update Requirements

## Gemini CLI Integration

### Strategic Command Usage
Use Gemini CLI operations judiciously:

```bash
# Only when needed:
./scripts/sdd/validate-spec.sh [feature]  # Complex/new specifications
./scripts/sdd/check-drift.sh [feature]    # Existing features with potential drift
./scripts/sdd/generate-from-spec.sh [feature]  # New feature scaffolding
```

### Integration with Cursor
When Cursor AI needs to run spec-kit operations:
```
@cursor: Execute Gemini CLI validation for [feature] (only if complex)
@cursor: Generate code structure from [feature] specification (only for new features)
@cursor: Check specification drift for [feature] (only for existing features)
```

## Post-Planning Actions

After plan creation:
1. **Validate Plan**: Ensure all spec scenarios are covered
2. **Update Tracking**: Add to specification tracking system
3. **Schedule Reviews**: Set up spec validation checkpoints
4. **Monitor Drift**: Enable continuous spec monitoring

## Best Practices

1. **Specification First**: Never plan without assessing specifications
2. **Maintain Sync**: Keep specs and plans synchronized at phase checkpoints
3. **Validate Strategically**: Run validation only when needed (complex specs, new features)
4. **Document Changes**: Update specs when requirements evolve
5. **Cross-Platform**: Ensure plans cover all platforms consistently
6. **Phase-Based Development**: Follow the 4-phase methodology for consistent delivery
7. **Incremental Validation**: Validate at phase boundaries, not continuously