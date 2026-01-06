# PLAIN Implementation - Quick Start Guide

**Everything you need to start building PLAIN with AI assistance.**

---

## What You Have

Six comprehensive documents to guide PLAIN implementation:

### 1. **README.md** - START HERE
Your master guide explaining the whole documentation system.

### 2. **language_spec.md** (67 KB) - THE SPEC
Complete language specification - the source of truth.

### 3. **implementation_guide.md** (17 KB) - WORK PLAN  
Phase-by-phase implementation roadmap with AI prompts.

### 4. **quick_reference.md** (10 KB) - CHEAT SHEET
Fast syntax lookup and implementation reminders.

### 5. **testing_strategy.md** (17 KB) - TEST GUIDE
Test templates and comprehensive testing approach.

### 6. **session_log.md** (9 KB) - PROGRESS TRACKER
Template for tracking work across sessions.

---

## Your First Steps

### Right Now (5 minutes)

1. **Read README.md** - Understand the documentation structure
2. **Skim language_spec.md** - Get a feel for PLAIN
3. **Review implementation_guide.md Phase 1** - See what's first

### Before First Coding Session (30 minutes)

1. **Setup Go project** structure (see implementation_guide.md)
2. **Read language_spec.md** core sections:
   - Design Philosophy
   - Keywords
   - Tasks
   - Variables
   - Control Structures

3. **Initialize session_log.md** - Start Session 1 entry

### Your First AI Prompt

```
I'm implementing PLAIN (Programming Language - Able, Intuitive, and Natural) in Go.

Complete specification: language_spec.md
Implementation guide: implementation_guide.md

Phase 1: Lexer (Tokenization)

According to the spec, PLAIN keywords include:
task, var, fxd, if, then, else, loop, from, to, in, 
deliver, abort, attempt, handle, ensure, record, use, etc.

Please help me:
1. Define Go token types for all PLAIN keywords
2. Create initial lexer structure
3. Implement basic keyword recognition

Reference: language_spec.md section "Reserved Keywords"
```

---

## Document Usage Guide

### When To Use Each Document

**Starting a session?**
→ session_log.md (restore context)
→ README.md (remind yourself of workflow)

**Implementing a feature?**
→ language_spec.md (understand requirements)
→ implementation_guide.md (get approach)
→ quick_reference.md (check syntax details)

**Writing tests?**
→ testing_strategy.md (get templates)
→ language_spec.md (verify expected behavior)

**Need quick syntax check?**
→ quick_reference.md (fast lookup)

**Ending a session?**
→ session_log.md (record progress)

---

## AI Assistant Strategy

### Maximum Context Prompts

**Session Start Template:**
```
I'm implementing PLAIN (see language_spec.md).

Current phase (from session_log.md): [Phase name]

Last completed: [Recent work from log]

Today's goal: [What you want to accomplish]

Specific task: [Detailed request]

Relevant spec section: [Quote from language_spec.md]

Please help me: [Specific question]
```

### Feature Implementation Template:**
```
Implementing [FEATURE] for PLAIN.

Spec says (language_spec.md):
"""
[Quote exact requirement]
"""

Implementation approach (implementation_guide.md):
- [Guidance point 1]
- [Guidance point 2]

Please create:
[Specific deliverable]

Must handle:
- [Requirement 1]
- [Error case 1]
```

### Testing Template:
```
Need tests for [COMPONENT].

Spec behavior (language_spec.md):
[Quote expected behavior]

Test template (testing_strategy.md):
[Show relevant template]

Generate tests for:
1. Happy path: [scenario]
2. Errors: [scenarios]
3. Edge cases: [scenarios]
```

---

## Critical Implementation Reminders

From language_spec.md:

✓ **No shadowing** - Can't redeclare variables in inner scopes  
✓ **No lambdas** (v1.0) - Use named tasks only  
✓ **Indentation matters** - Like Python, defines blocks  
✓ **Parameters immutable** - Can't assign to task params  
✓ **Module scope ≠ global** - Module vars only visible in module  
✓ **Explicit errors** - Clear messages with location  

---

## Testing Priority

From testing_strategy.md:

1. **Lexer** - All token types
2. **Parser** - Each construct + precedence  
3. **Type system** - Inference + validation
4. **Runtime** - Execution + errors
5. **Stdlib** - Each function
6. **Integration** - Full programs

Target: **>80% coverage** for each component

---

## Progress Tracking

Update session_log.md after each session:

```markdown
### Session X: [DATE]

**Goal:** [What you wanted to do]

**Completed:**
- [x] Task 1
- [x] Task 2

**In Progress:**
- Task 3 - [status]

**Next Session:**
- [ ] Continue task 3
- [ ] Start task 4

**Notes:** [Important observations]
```

---

## Implementation Phases

From implementation_guide.md:

1. **Lexer** - Tokenization (1-2 weeks)
2. **Parser** - AST construction (2-3 weeks)
3. **Symbol Table** - Scope management (1 week)
4. **Type System** - Type checking (1-2 weeks)
5. **Runtime** - Interpreter (2-3 weeks)
6. **Standard Library** - Built-in functions (2-3 weeks)
7. **File I/O** - File operations (1 week)
8. **Events** - Timer system (1 week)
9. **REPL** - Interactive mode (1 week)
10. **Integration** - Testing & polish (1-2 weeks)

**Total estimate:** 3-4 months of focused work

---

## Common Questions

**Q: Which doc is most important?**  
A: language_spec.md - it's the source of truth

**Q: Do I need to read everything first?**  
A: No, read README.md, then dive in. Reference others as needed.

**Q: What if the spec is ambiguous?**  
A: Note in session_log, make reasonable choice, document decision, continue.

**Q: Should I use TDD?**  
A: When practical, yes. At minimum, write tests as you implement.

**Q: How do I keep AI on track?**  
A: Always provide context from session_log and quote from language_spec.

**Q: What if I disagree with the spec?**  
A: Note it, but implement as spec'd. Suggest changes after v1.0.

---

## Success Checklist

### For Each Feature:
- [ ] Read spec section
- [ ] Check implementation guide
- [ ] Write tests first (when possible)
- [ ] Implement feature
- [ ] Verify tests pass
- [ ] Update session_log
- [ ] Commit with good message

### For Each Session:
- [ ] Start: Review session_log
- [ ] Plan: Specific achievable goal
- [ ] Work: Implement + test
- [ ] Document: Update session_log
- [ ] Set: Next session goals

### For Overall Progress:
- [ ] Follow phases in order
- [ ] Maintain >80% test coverage
- [ ] Keep session_log current
- [ ] Reference spec constantly
- [ ] Ask for help when stuck

---

## Your First Task

**Concrete first step:**

1. **Setup Go project:**
```bash
mkdir plain
cd plain
go mod init github.com/yourusername/plain
mkdir -p cmd/plain internal/lexer internal/parser
```

2. **Create first file:** `internal/lexer/token.go`

3. **Use this AI prompt:**
```
I'm implementing PLAIN's lexer. First file: token.go

From language_spec.md, PLAIN has these keyword categories:
- Task-related: task, with, using, deliver, abort
- Variables: var, fxd, as
- Control: if, then, else, choose, choice, default, loop, from, to, in, exit, continue
- Error handling: attempt, handle, ensure
- Modules: use:, assemblies:, modules:, tasks:
- Types: record, based, on
- Comments: rem:, note:
- Type names: int/integer, flt/float, str/string, bln/boolean, lst/list, tbl/table
- Literals: null, true, false
- Operators: and, or, not

Please create token.go with:
1. Token type enum for all keywords
2. Token struct with Type, Value, Line, Column
3. Keyword map for quick lookup

Follow Go best practices.
```

---

## Resources at Your Fingertips

**Every question answered:**
- Syntax? → quick_reference.md
- How to implement? → implementation_guide.md
- Expected behavior? → language_spec.md
- How to test? → testing_strategy.md
- Where am I? → session_log.md
- How does it fit? → README.md

---

## Final Encouragement

You have everything you need:
- ✓ Complete specification
- ✓ Implementation roadmap
- ✓ Testing strategy
- ✓ AI prompt templates
- ✓ Progress tracking system

**Now go build PLAIN! 🚀**

Start small, test constantly, reference docs frequently, document progress.

Good luck!

---

**Next step:** Open README.md and read the full documentation guide.

**After that:** Begin Phase 1 - Lexer implementation.

**Remember:** The docs are your friends. Use them!
