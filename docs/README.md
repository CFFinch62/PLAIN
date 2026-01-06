# PLAIN Language - Implementation Documentation

**Welcome to the PLAIN implementation project!**

This documentation suite is designed to help you (and AI assistants) build the PLAIN programming language efficiently and consistently across multiple sessions.

---

## What is PLAIN?

**PLAIN** = **P**rogramming **L**anguage - **A**ble, **I**ntuitive, and **N**atural

PLAIN is a programming language designed to be:
- **Able** - Competent enough for real work
- **Intuitive** - Easy to understand and learn
- **Natural** - Reads like plain English where possible

**Target Users:**
- Students learning programming
- Educators teaching fundamentals
- Developers wanting clarity over cleverness
- Marine electronics applications (creator's domain)

**Implementation Language:** Go

---

## Documentation Structure

### 1. `language_spec.md` ⭐ PRIMARY REFERENCE
**The source of truth for PLAIN's design.**

Contains complete specification of:
- Syntax and keywords
- Type system
- Control structures
- Error handling
- Modules and imports
- Records (custom types)
- Scope rules
- Standard library
- File I/O
- Concurrency/events
- Operator precedence

**When to use:** 
- Before implementing any feature
- When answering "how should X work?"
- When writing tests
- When resolving ambiguities
- ALWAYS reference this first

**How to use with AI:**
```
According to language_spec.md section [X]:
[Quote relevant part]

I need to implement [feature]. 
[Ask specific question]
```

---

### 2. `implementation_guide.md` 📋 WORK PLAN
**Your roadmap for building PLAIN.**

Contains:
- Implementation phases (lexer → parser → runtime → stdlib)
- Structured prompts for AI assistance
- Component-specific guidance
- Testing strategies
- Common pitfalls
- Session handoff templates

**When to use:**
- Starting a new implementation phase
- Need AI assistance prompt templates
- Planning what to build next
- Unsure how to approach a component

**How to use with AI:**
```
I'm starting Phase [N]: [Component] from implementation_guide.md.

Today's task: [Specific goal]

Please help me: [Specific request]
```

---

### 3. `quick_reference.md` 🚀 CHEAT SHEET
**Fast lookup for PLAIN syntax and rules.**

Contains:
- All keywords at a glance
- Syntax templates
- Operator precedence table
- Stdlib function signatures
- Common patterns
- Implementation reminders

**When to use:**
- Quick syntax lookup
- Verify operator precedence
- Check stdlib function signature
- Remind yourself of rules (no shadowing, etc.)
- Generate example code

**How to use:**
- Keep open while coding
- Reference when writing tests
- Use as quick verification

---

### 4. `testing_strategy.md` ✅ TEST GUIDE
**Comprehensive testing approach.**

Contains:
- Test case templates
- Unit test examples
- Integration test patterns
- E2E test scenarios
- Error message tests
- Coverage goals

**When to use:**
- Writing tests for new feature
- Checking test coverage
- Debugging failing tests
- Planning test cases

**How to use with AI:**
```
I need tests for [component].

According to testing_strategy.md, I should test:
1. Happy path
2. Error cases
3. Edge cases

Please generate tests for [specific scenarios].
```

---

### 5. `session_log.md` 📝 PROGRESS TRACKER
**Track implementation progress across sessions.**

Contains:
- Session history template
- Phase completion checklists
- Issue tracking
- Decision log
- Performance notes
- Technical debt tracker

**When to use:**
- Start of each session (restore context)
- End of each session (record progress)
- Track decisions and issues
- Monitor overall progress

**How to update:**
After each session, fill out:
```markdown
### Session X: [DATE]
**Goal:** [What you wanted to accomplish]
**Completed:** [What you finished]
**In Progress:** [What's partially done]
**Next Session:** [What to do next]
```

**How to use with AI (start of session):**
```
I'm implementing PLAIN. See session_log.md for current status.

Last session completed: [List]
Today I want to: [Goal]

Please help me: [Specific request]
```

---

## Getting Started

### For Your First Session

1. **Read `language_spec.md`** (at least sections relevant to Phase 1)
2. **Review `implementation_guide.md` Phase 1: Lexer**
3. **Setup project structure** (see implementation_guide.md)
4. **Initialize `session_log.md`** with Session 1

### Starting the Lexer

**Prompt for AI:**
```
I'm starting to implement PLAIN (see language_spec.md) in Go.

Phase 1: Lexer implementation

According to the spec, PLAIN has these keywords:
[List from quick_reference.md]

I need to:
1. Define token types
2. Implement basic tokenization
3. Handle indentation (Python-style)

Please help me create the token type definitions and initial lexer structure.
```

### Typical Session Flow

1. **Restore Context**
   - Review session_log.md
   - Check what was completed
   - Note any blockers

2. **Plan Today's Work**
   - Pick specific component/feature
   - Review spec for that feature
   - Check implementation_guide for approach

3. **Implement**
   - Write code (with AI help)
   - Reference spec frequently
   - Follow testing_strategy

4. **Test**
   - Write tests as you go (TDD when possible)
   - Use testing_strategy.md templates
   - Aim for >80% coverage

5. **Document**
   - Update session_log.md
   - Note decisions made
   - Record any issues
   - Set next session goals

6. **Commit**
   - Good commit messages
   - Reference spec sections
   - Note what tests were added

---

## AI Assistant Best Practices

### Context Restoration (Start of Session)

```
I'm implementing PLAIN (Programming Language - Able, Intuitive, Natural) in Go.

Key docs:
- language_spec.md = complete specification
- implementation_guide.md = implementation roadmap  
- session_log.md = current progress

Current status (from session_log.md):
- Phase: [Current phase]
- Last completed: [Recent work]
- In progress: [Current task]

Today's goal: [What you want to accomplish]

Please help me: [Specific request]
```

### When Implementing a Feature

```
I'm implementing [FEATURE] for PLAIN.

According to language_spec.md:
[Quote relevant section]

Implementation approach (from implementation_guide.md):
[Quote relevant guidance]

Please help me implement [SPECIFIC COMPONENT] that:
- [Requirement 1]
- [Requirement 2]

Error cases to handle:
- [Error 1]
- [Error 2]
```

### When Writing Tests

```
I need tests for [COMPONENT].

According to language_spec.md:
[Quote behavior specification]

Test template (from testing_strategy.md):
[Show relevant template]

Please create tests covering:
1. Happy path: [Scenario]
2. Error cases: [Scenarios]
3. Edge cases: [Scenarios]
```

### When Debugging

```
I'm seeing [PROBLEM] in [COMPONENT].

Expected (from spec): [Behavior]
Actual: [What's happening]

Code:
[Show relevant code]

What's wrong?
```

### When Clarifying Spec

```
The spec says [QUOTE] in language_spec.md.

Does this mean [INTERPRETATION A] or [INTERPRETATION B]?

Example code:
[Show example]

How should this behave?
```

---

## Common Workflows

### Adding a New Feature

1. ✓ Check if it's in the spec
2. ✓ Read spec section thoroughly
3. ✓ Check implementation_guide for approach
4. ✓ Write tests first (TDD)
5. ✓ Implement feature
6. ✓ Verify tests pass
7. ✓ Update session_log
8. ✓ Commit with clear message

### Debugging an Issue

1. ✓ Write failing test that reproduces issue
2. ✓ Check spec for expected behavior
3. ✓ Review implementation_guide for common pitfalls
4. ✓ Debug with AI assistance
5. ✓ Fix and verify test passes
6. ✓ Add to session_log issues (if pattern worth noting)

### Completing a Phase

1. ✓ Check phase checklist in session_log
2. ✓ Verify all tests passing
3. ✓ Review test coverage (>80% goal)
4. ✓ Update session_log status
5. ✓ Review implementation_guide for next phase
6. ✓ Plan first task of next phase

---

## Key Design Principles (Reminders)

### From the Spec

1. **No shadowing** - Variables cannot be redeclared in inner scopes
2. **No lambdas** (v1.0) - Use named tasks only
3. **Indentation-based blocks** - Like Python
4. **Explicit over implicit** - `var` declares, no `var` assigns
5. **Tasks are procedures or functions**
   - `task Name()` - no params, no return
   - `task Name with (params)` - params, no return
   - `task Name using (inputs)` - params, must deliver

6. **Parameters are immutable** - Cannot assign to task parameters
7. **Module scope is not global** - Module variables only visible within module
8. **Error messages should be helpful** - Always include location and context

### Implementation Constraints

1. **Use Go idiomatically** - Leverage Go's strengths
2. **Test as you go** - TDD when practical
3. **Reference spec constantly** - It's the source of truth
4. **Document decisions** - Update session_log
5. **Clear error messages** - Follow format: [what] [where] [(why/fix)]

---

## File Organization

```
plain/                              # Project root
├── docs/                           # This documentation
│   ├── README.md                   # This file
│   ├── language_spec.md            # Complete specification
│   ├── implementation_guide.md     # Implementation roadmap
│   ├── quick_reference.md          # Syntax cheat sheet
│   ├── testing_strategy.md         # Test approach
│   └── session_log.md              # Progress tracker
│
├── cmd/                            # Executables
│   ├── plain/                      # Interpreter
│   │   └── main.go
│   └── plainc/                     # Compiler (future)
│
├── internal/                       # Implementation packages
│   ├── lexer/                      # Tokenization
│   ├── parser/                     # AST construction
│   ├── ast/                        # AST definitions
│   ├── types/                      # Type system
│   ├── scope/                      # Symbol tables
│   ├── runtime/                    # Interpreter
│   ├── stdlib/                     # Standard library
│   ├── fileio/                     # File operations
│   └── events/                     # Timer/event system
│
├── pkg/                            # Public API
│   └── plain/
│
├── examples/                       # Example PLAIN programs
│   ├── hello.plain
│   ├── fibonacci.plain
│   └── ...
│
├── tests/                          # Test suite
│   ├── lexer_test.go
│   ├── parser_test.go
│   └── ...
│
├── go.mod                          # Go module file
├── go.sum                          # Go dependencies
└── README.md                       # Project README
```

---

## Quick Command Reference

### Start New Session
```
Open: session_log.md
Review: Last session notes
Update: Session X template with today's date
Plan: Today's specific goal
```

### Implement Feature
```
Read: language_spec.md section for feature
Review: implementation_guide.md for approach
Write: Tests first (testing_strategy.md)
Code: Implementation
Verify: Tests pass
Update: session_log.md
```

### Get AI Help
```
Provide: Context from session_log.md
Quote: Relevant spec section
Ask: Specific question
Show: Relevant code if debugging
```

### End Session
```
Update: session_log.md with progress
Commit: With clear message
Note: Next session goals
Save: Any decisions or issues
```

---

## Version History

**v1.0** - Initial documentation suite
- Complete language specification
- Implementation guide with prompts
- Quick reference card
- Testing strategy
- Session tracking system

---

## Support & Resources

### When Stuck

1. Re-read relevant spec section
2. Check implementation_guide common pitfalls
3. Review quick_reference for syntax
4. Search session_log for similar issues
5. Ask AI with proper context

### Questions About Spec

If spec is ambiguous:
1. Note in session_log
2. Make reasonable assumption
3. Document decision
4. Continue implementation
5. Can clarify later if needed

### Performance Issues

1. First: make it work correctly
2. Then: make it work well
3. Profile before optimizing
4. Document performance notes in session_log

---

## Success Metrics

### Code Quality
- [ ] Follows spec exactly
- [ ] >80% test coverage
- [ ] Clear, helpful error messages
- [ ] Idiomatic Go code
- [ ] Well-documented

### Progress Tracking
- [ ] Session log kept up to date
- [ ] Decisions documented
- [ ] Issues tracked
- [ ] Milestones clear

### AI Effectiveness
- [ ] Context provided in each session
- [ ] Spec referenced appropriately
- [ ] Prompts are specific
- [ ] Progress is steady

---

## Next Steps

**Your immediate next steps:**

1. **Read `language_spec.md`** - At least overview
2. **Set up Go project** - Use structure from implementation_guide
3. **Initialize `session_log.md`** - Fill in Session 1
4. **Start Phase 1: Lexer** - Follow implementation_guide
5. **Use AI assistance** - With context from docs

**First concrete task:**

Start with lexer token definitions. Use this prompt:

```
I'm implementing PLAIN (see language_spec.md) in Go.

Starting Phase 1: Lexer (from implementation_guide.md).

PLAIN's keywords (from quick_reference.md):
task, var, fxd, if, loop, etc.

Please help me:
1. Define token types for all keywords
2. Create basic lexer structure
3. Implement keyword recognition

Let's start with token type definitions.
```

---

## Remember

- **Spec is truth** - Always reference language_spec.md
- **Document as you go** - Update session_log.md
- **Test early and often** - Use testing_strategy.md
- **Context matters** - Give AI full picture
- **Iterate steadily** - Small steps, constant progress

Good luck building PLAIN! 🚀

---

**Documentation maintained by:** Chuck  
**Project:** PLAIN Language Implementation  
**Started:** January 2026  
**Status:** Ready to begin implementation
