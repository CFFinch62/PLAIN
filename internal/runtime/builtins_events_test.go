package runtime

import (
	"testing"
	"time"
)

// TestSleep tests the sleep function
func TestSleep(t *testing.T) {
	builtins := GetBuiltins()

	start := time.Now()
	result := builtins["sleep"].Fn(NewInteger(100))
	elapsed := time.Since(start)

	if _, ok := result.(*NullValue); !ok {
		t.Errorf("sleep should return null, got %s", result.Type())
	}

	if elapsed < 90*time.Millisecond {
		t.Errorf("sleep should have waited at least 90ms, waited %v", elapsed)
	}
}

// TestCreateTimer tests timer creation
func TestCreateTimer(t *testing.T) {
	GetEventLoop().Reset()
	builtins := GetBuiltins()

	// Need a TaskValue for callback
	callback := &TaskValue{
		Name:       "TestCallback",
		Parameters: []string{},
	}

	result := builtins["create_timer"].Fn(NewInteger(100), callback)
	timer, ok := result.(*TimerValue)
	if !ok {
		t.Fatalf("create_timer should return TimerValue, got %s", result.Type())
	}

	if timer.Running {
		t.Error("timer should not be running initially")
	}
	if timer.IsOneShot {
		t.Error("timer should not be one-shot")
	}
	if timer.Interval != 100 {
		t.Errorf("timer interval should be 100, got %d", timer.Interval)
	}
}

// TestCreateTimeout tests timeout creation
func TestCreateTimeout(t *testing.T) {
	GetEventLoop().Reset()
	builtins := GetBuiltins()

	callback := &TaskValue{
		Name:       "TestCallback",
		Parameters: []string{},
	}

	result := builtins["create_timeout"].Fn(NewInteger(500), callback)
	timer, ok := result.(*TimerValue)
	if !ok {
		t.Fatalf("create_timeout should return TimerValue, got %s", result.Type())
	}

	if timer.Running {
		t.Error("timeout should not be running initially")
	}
	if !timer.IsOneShot {
		t.Error("timeout should be one-shot")
	}
}

// TestStartStopTimer tests timer start/stop
func TestStartStopTimer(t *testing.T) {
	GetEventLoop().Reset()
	builtins := GetBuiltins()

	callback := &TaskValue{
		Name:       "TestCallback",
		Parameters: []string{},
	}

	timer := builtins["create_timer"].Fn(NewInteger(100), callback).(*TimerValue)

	// Start timer
	builtins["start_timer"].Fn(timer)
	if !timer.Running {
		t.Error("timer should be running after start_timer")
	}

	// Stop timer
	time.Sleep(50 * time.Millisecond)
	builtins["stop_timer"].Fn(timer)
	time.Sleep(50 * time.Millisecond) // Wait for goroutine to stop
	if timer.Running {
		t.Error("timer should not be running after stop_timer")
	}
}

// TestCancelTimer tests timer cancellation
func TestCancelTimer(t *testing.T) {
	GetEventLoop().Reset()
	builtins := GetBuiltins()

	callback := &TaskValue{
		Name:       "TestCallback",
		Parameters: []string{},
	}

	timer := builtins["create_timer"].Fn(NewInteger(100), callback).(*TimerValue)
	builtins["start_timer"].Fn(timer)

	// Cancel timer
	builtins["cancel_timer"].Fn(timer)
	time.Sleep(50 * time.Millisecond)

	if !timer.Cancelled {
		t.Error("timer should be cancelled after cancel_timer")
	}
}

// TestRunEvents tests run_events with duration
func TestRunEvents(t *testing.T) {
	GetEventLoop().Reset()
	builtins := GetBuiltins()

	start := time.Now()
	builtins["run_events"].Fn(NewInteger(200))
	elapsed := time.Since(start)

	if elapsed < 180*time.Millisecond {
		t.Errorf("run_events should have run for ~200ms, ran for %v", elapsed)
	}
}

// TestEventFunctionErrors tests error handling
func TestEventFunctionErrors(t *testing.T) {
	builtins := GetBuiltins()

	// sleep with wrong type
	result := builtins["sleep"].Fn(NewString("not a number"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("sleep should error with wrong argument type")
	}

	// start_timer with wrong type
	result = builtins["start_timer"].Fn(NewString("not a timer"))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("start_timer should error with wrong argument type")
	}

	// create_timer with wrong args
	result = builtins["create_timer"].Fn(NewInteger(100))
	if _, ok := result.(*ErrorValue); !ok {
		t.Error("create_timer should error with wrong number of args")
	}
}
