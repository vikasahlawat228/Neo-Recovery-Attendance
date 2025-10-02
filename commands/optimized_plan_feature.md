Note: you may tweak the instructions mentioned within this plan doc as per the nature of the feature and as per the best recommendations for an industrial standard feature plan implementation.

The user will provide a feature description. Your job is to:

1. Create a technical plan that concisely describes the feature the user wants to build.                                                                        
2. Research the files and functions that need to be changed to implement the feature                                                                            
3. Avoid any product manager style sections (no success criteria, timeline, migration, etc)                                                                     
4. Avoid writing any actual code in the plan.
5. Include specific and verbatim details from the user's prompt to ensure the plan is accurate.                                                                 
6. Once go through the current codebase to understand the current implementation.                                                                               

This is strictly a technical requirements document that should:
1. Include a brief description to set context at the top
2. Point to all the relevant files and functions that need to be changed or created                                                                             
3. Explain any algorithms that are used step-by-step
4. If necessary, breaks up the work into logical phases. Ideally this should be done in a way that has an initial "data layer" phase that defines the types and db changes that need to run, followed by N phases that can be done in parallel (e.g. Phase 2A - UI, Phase 2B - API, Phase 3: Integration). Only include phases if it's a REALLY big feature.                                                    

If the user's requirements are unclear, especially after researching the relevant files, you may ask up to 5 clarifying questions before writing the plan. If you do so, incorporate the user's answers into the plan.                          

Prioritize being concise and precise. Make the plan as tight as possible without losing any of the critical details from the user's requirements.               

Write the plan into an docs/features/<N>_PLAN.md file with the next available feature number (starting with 0001)

---

## Cursor Agent Orchestration

After you generate the plan, append a comprehensive section titled "Cursor Agent Orchestration" that includes the complete agent prompts from AGENT_PROMPT_TEMPLATES.md. For each phase in your plan, include the full agent prompt template customized for that specific feature.

### Agent Commands with Full Prompts

**Planning & Analysis**
- `@analyze_plan: "Read the plan and append implementation analysis to the plan file"`

**Phase Implementation Commands** (include full agent prompts below):

#### Phase 1: Data Layer Implementation
```bash
@agent: "You are the Data Layer Agent. Implement Phase 1 data foundation for [FEATURE_NAME]:

**Task**: Create/modify data layer components

**Files to Focus On**:
- packages/shared/src/types/[feature].ts
- packages/shared/src/schemas/[feature].schema.ts
- apps/api/src/migrations/[timestamp]-[name].ts
- apps/api/src/entities/[entity].entity.ts

**Implementation Requirements**:
- Create TypeScript types with strict typing
- Add Zod schemas for runtime validation
- Generate TypeORM migrations (timestamped, reversible)
- Update entity definitions with proper relationships
- Export types from packages/shared/index.ts

**Constraints**:
- Preserve existing formatting and imports
- Follow existing naming conventions
- No UI or API logic
- Focus only on data layer files
- Ensure type safety across all apps"
```

#### Phase 2A: UI Implementation
```bash
@agent: "You are the UI Agent. Implement Phase 2A UI components for [FEATURE_NAME]:

**Task**: Create/modify UI components

**Files to Focus On**:
- apps/admin/src/app/[feature]/page.tsx
- apps/admin/src/components/[feature]/[Component].tsx
- apps/mobile/src/screens/[feature]/[Screen].tsx
- apps/mobile/src/components/[feature]/[Component].tsx

**Implementation Requirements**:
- **Admin**: Use shadcn/ui components, Tailwind CSS, Next.js patterns
- **Mobile**: Use NativeWind styling, Expo patterns, React Native components
- Ensure accessibility (a11y) compliance
- Keep props typed and consistent
- Match existing design patterns
- Add proper navigation integration

**Constraints**:
- No business logic implementation
- Focus only on UI files
- Preserve existing styling patterns
- Ensure responsive design
- Follow component composition patterns"
```

#### Phase 2B: API Implementation
```bash
@agent: "You are the API Agent. Implement Phase 2B API layer for [FEATURE_NAME]:

**Task**: Create/modify API components

**Files to Focus On**:
- apps/api/src/[feature]/services/[feature].service.ts
- apps/api/src/[feature]/controllers/[feature].controller.ts
- apps/api/src/[feature]/dto/[feature].dto.ts
- apps/api/src/[feature]/[feature].module.ts

**Implementation Requirements**:
- Create NestJS services with business logic
- Add controllers with proper DTOs
- Implement validation with class-validator
- Add proper error handling and guards
- Follow existing API patterns
- Add Swagger documentation

**Constraints**:
- No UI or data layer changes
- Focus only on API files
- Follow existing service patterns
- Ensure proper error handling
- Add comprehensive validation"
```

#### Phase 3: Integration & Testing
```bash
@agent: "You are the Integration & Tests Agent. Implement Phase 3 integration for [FEATURE_NAME]:

**Task**: Create tests and integration code

**Files to Focus On**:
- apps/api/src/[feature]/__tests__/[feature].service.spec.ts
- apps/api/src/[feature]/__tests__/[feature].controller.spec.ts
- apps/mobile/src/screens/[feature]/__tests__/[Screen].test.tsx
- apps/admin/src/app/[feature]/__tests__/[Component].test.tsx

**Implementation Requirements**:
- Add unit tests for new functionality
- Create integration tests for cross-app features
- Update documentation (README, API docs)
- Wire together UI and API components
- Ensure 80%+ test coverage
- Add E2E test scenarios

**Constraints**:
- Focus on testing and integration only
- Ensure comprehensive test coverage
- Follow existing test patterns
- Update documentation accurately
- Verify cross-app functionality"
```

### Review & Fix Commands

#### Review Commands
```bash
@agent: "You are the Review Agent. Use the @code_review.md prompt to thoroughly review the [PHASE_NAME] implementation for [FEATURE_NAME]:

**Task**: Comprehensive code review using @code_review.md standards

**Review Focus** (from @code_review.md):
1. **Plan Implementation**: Make sure the plan was correctly implemented
2. **Obvious Bugs**: Look for any obvious bugs or issues in the code
3. **Data Alignment**: Look for subtle data alignment issues (snake_case vs camelCase, nested objects like {data:{}})
4. **Over-engineering**: Look for over-engineering or files getting too large needing refactoring
5. **Style Consistency**: Look for weird syntax or style that doesn't match other parts of the codebase

**Output**: Create docs/features/[N]_REVIEW.md with detailed findings and specific fixes needed

**Constraints**:
- Follow @code_review.md format exactly
- Provide specific file locations and line numbers
- Suggest concrete fixes for each issue
- Consider maintainability and production readiness"
```

#### Fix Commands
```bash
@agent: "You are the Fix Agent. Implement all fixes from the review document for [FEATURE_NAME]:

**Task**: Read docs/features/[N]_REVIEW.md and implement all identified fixes

**Requirements**:
- Address every issue listed in the review document
- Maintain existing functionality
- Follow project conventions and patterns
- Preserve code formatting and style
- Add tests for new fixes where needed
- Verify fixes resolve the review issues

**Implementation Approach**:
- Fix issues in order of severity (critical → minor)
- Test each fix before moving to the next
- Ensure no regressions are introduced
- Update documentation if needed

**Output**: Implement all fixes and provide summary of changes made

**Constraints**:
- Don't add new features beyond what's needed for fixes
- Maintain backward compatibility
- Follow existing code patterns
- Ensure all fixes are properly tested"
```

### Model Selection Guidelines
- **Auto Mode**: Simple CRUD, boilerplate, imports (<50 LOC)
- **Gemini Pro**: UI/UX, creative work, styling
- **Claude Sonnet**: TypeScript types, business logic, architecture
- **GPT-4o**: Complex algorithms, integrations, debugging

### Quality Checkpoints
After each phase: `yarn lint && yarn typecheck && yarn test`
After review fixes: `yarn lint && yarn typecheck && yarn test && yarn build`

### Template Integration Notes
- All agent prompts are automatically included in generated feature plans
- Each `@implement_phase_X` command references the complete agent prompt from the plan
- No need to manually copy templates - everything is pre-configured in the plan
- Customize [FEATURE_NAME] and file paths for each specific feature implementation