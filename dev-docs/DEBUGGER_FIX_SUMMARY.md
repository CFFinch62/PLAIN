# Debugger Stepping Fixes

## Issues Fixed

### 1. Loop Stepping Not Working
**Problem**: The debugger would not step through individual loop iterations. When stepping through a loop, it would only stop once at the first iteration and then skip to after the loop.

**Root Cause**: 
- The `evalLoopDebug` function was delegating to the regular evaluator instead of using debug hooks
- The `onStatement` function was skipping statements on the same line, which prevented stepping through loop iterations

**Fix**:
- Implemented full loop evaluation in `evalLoopDebug` with proper debug hooks for all loop types:
  - Counting loops (`loop i from 1 to 10`)
  - Iteration loops (`loop item in list`)
  - Conditional loops (`loop condition`)
  - Infinite loops
- Modified `onStatement` to only skip same-line statements in `DebugRun` mode, not in step modes

### 2. Function Call Stepping Not Working
**Problem**: The debugger would not step into user-defined helper functions. It would step over them instead.

**Root Cause**: 
- Expression statements containing function calls were being evaluated by the regular evaluator
- The regular evaluator's `applyFunction` was being used instead of `applyFunctionDebug`

**Fix**:
- Added `evalExpressionDebug` to intercept expression evaluation
- Added `evalCallExpressionDebug` to handle function calls with debug hooks
- Modified `evalStatementDebug` to intercept:
  - `ExpressionStatement` (for standalone function calls)
  - `VarStatement` (for `var x = Helper()`)
  - `AssignStatement` (for `x = Helper()`)
  - `DeliverStatement` (for `deliver Helper()`)
- Function calls now properly push/pop call stack frames and use `applyFunctionDebug`

## Files Modified

- `internal/runtime/debugger.go`:
  - `onStatement()` - Fixed same-line skipping logic
  - `evalLoopDebug()` - Implemented full loop debugging
  - `evalStatementDebug()` - Added interception for more statement types
  - `evalExpressionDebug()` - New function to intercept expressions
  - `evalCallExpressionDebug()` - New function to handle function calls
  - `evalVarStatementDebug()` - New function for variable declarations
  - `evalAssignStatementDebug()` - New function for assignments
  - `evalDeliverStatementDebug()` - New function for return statements

## Testing

Created `examples/basic/debug_test.plain` to demonstrate both fixes:
- Loop stepping: Stops at each iteration of a loop
- Function stepping: Steps into helper functions

Test results:
- ✅ Loop stepping: Stops 3 times at line 16 (once per iteration)
- ✅ Function stepping: Successfully steps into Helper function with proper call stack

## Impact

These fixes are critical for students learning programming, as a proper stepping debugger is essential for:
- Understanding loop execution flow
- Tracing function calls
- Debugging logic errors
- Learning how code executes step-by-step

