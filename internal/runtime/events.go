package runtime

import (
	"sync"
	"time"
)

// EventLoop manages timers and the event loop
type EventLoop struct {
	timers     map[int]*TimerValue
	timerStops map[int]chan struct{}
	nextID     int
	running    bool
	stopChan   chan struct{}
	mu         sync.Mutex
	evaluator  interface{} // *Evaluator - set when running
	wg         sync.WaitGroup
}

// Global event loop singleton
var globalEventLoop = &EventLoop{
	timers:     make(map[int]*TimerValue),
	timerStops: make(map[int]chan struct{}),
	nextID:     1,
}

// GetEventLoop returns the global event loop
func GetEventLoop() *EventLoop {
	return globalEventLoop
}

// SetEvaluator sets the evaluator for callback invocation
func (el *EventLoop) SetEvaluator(eval interface{}) {
	el.mu.Lock()
	defer el.mu.Unlock()
	el.evaluator = eval
}

// CreateTimer creates a new repeating timer
func (el *EventLoop) CreateTimer(intervalMs int64, callback *TaskValue) *TimerValue {
	el.mu.Lock()
	defer el.mu.Unlock()

	timer := &TimerValue{
		ID:        el.nextID,
		Interval:  intervalMs,
		Callback:  callback,
		IsOneShot: false,
		Running:   false,
		Cancelled: false,
	}
	el.nextID++
	el.timers[timer.ID] = timer
	el.timerStops[timer.ID] = make(chan struct{})
	return timer
}

// CreateTimeout creates a one-shot timer
func (el *EventLoop) CreateTimeout(delayMs int64, callback *TaskValue) *TimerValue {
	el.mu.Lock()
	defer el.mu.Unlock()

	timer := &TimerValue{
		ID:        el.nextID,
		Interval:  delayMs,
		Callback:  callback,
		IsOneShot: true,
		Running:   false,
		Cancelled: false,
	}
	el.nextID++
	el.timers[timer.ID] = timer
	el.timerStops[timer.ID] = make(chan struct{})
	return timer
}

// StartTimer starts a timer
func (el *EventLoop) StartTimer(timer *TimerValue) {
	el.mu.Lock()
	if timer.Running || timer.Cancelled {
		el.mu.Unlock()
		return
	}
	timer.Running = true
	stopChan := el.timerStops[timer.ID]
	el.wg.Add(1)
	el.mu.Unlock()

	go el.runTimer(timer, stopChan)
}

// StopTimer stops a timer (can be restarted)
func (el *EventLoop) StopTimer(timer *TimerValue) {
	el.mu.Lock()
	defer el.mu.Unlock()

	if !timer.Running {
		return
	}
	timer.Running = false
	if stopChan, ok := el.timerStops[timer.ID]; ok {
		close(stopChan)
		el.timerStops[timer.ID] = make(chan struct{})
	}
}

// CancelTimer stops and removes a timer
func (el *EventLoop) CancelTimer(timer *TimerValue) {
	el.mu.Lock()

	if timer.Running {
		timer.Running = false
		if stopChan, ok := el.timerStops[timer.ID]; ok {
			close(stopChan)
		}
	}
	timer.Cancelled = true
	delete(el.timers, timer.ID)
	delete(el.timerStops, timer.ID)
	el.mu.Unlock()
}

// runTimer runs the timer goroutine
func (el *EventLoop) runTimer(timer *TimerValue, stopChan chan struct{}) {
	defer el.wg.Done()

	startTime := time.Now()
	ticker := time.NewTicker(time.Duration(timer.Interval) * time.Millisecond)
	defer ticker.Stop()

	for {
		select {
		case <-stopChan:
			return
		case <-ticker.C:
			el.mu.Lock()
			if timer.Cancelled || !timer.Running {
				el.mu.Unlock()
				return
			}
			callback := timer.Callback.(*TaskValue)
			elapsed := time.Since(startTime).Milliseconds()
			el.mu.Unlock()

			// Execute callback
			el.executeCallback(timer, callback, elapsed)

			// If one-shot, stop after first execution
			if timer.IsOneShot {
				el.CancelTimer(timer)
				return
			}
		}
	}
}

// executeCallback invokes the timer callback
func (el *EventLoop) executeCallback(timer *TimerValue, callback *TaskValue, elapsedMs int64) {
	// Callback execution will be handled by the evaluator
	// This is a placeholder - the evaluator will be injected
	if el.evaluator != nil {
		if eval, ok := el.evaluator.(*Evaluator); ok {
			var result Value
			if len(callback.Parameters) >= 2 {
				// Pass timer and elapsed
				result = eval.callTask(callback, []Value{timer, NewInteger(elapsedMs)})
			} else {
				// Simple callback with no params
				result = eval.callTask(callback, []Value{})
			}
			// Handle errors in callback
			if err, ok := result.(*ErrorValue); ok {
				// Print error and cancel the timer
				eval.output("Timer error in " + callback.Name + ": " + err.Message + "\n")
				el.CancelTimer(timer)
			}
		}
	}
}

// WaitForEvents blocks until all timers complete
func (el *EventLoop) WaitForEvents() {
	el.mu.Lock()
	el.running = true
	el.stopChan = make(chan struct{})
	el.mu.Unlock()

	// Wait for all timer goroutines to complete
	el.wg.Wait()

	el.mu.Lock()
	el.running = false
	el.mu.Unlock()
}

// RunEvents runs the event loop for a specified duration
func (el *EventLoop) RunEvents(durationMs int64) {
	el.mu.Lock()
	el.running = true
	el.stopChan = make(chan struct{})
	el.mu.Unlock()

	// Wait for duration or until stopped
	select {
	case <-time.After(time.Duration(durationMs) * time.Millisecond):
	case <-el.stopChan:
	}

	el.mu.Lock()
	el.running = false
	el.mu.Unlock()
}

// StopEvents signals the event loop to stop
func (el *EventLoop) StopEvents() {
	el.mu.Lock()
	defer el.mu.Unlock()

	if el.running && el.stopChan != nil {
		close(el.stopChan)
		el.running = false
	}

	// Stop all active timers
	for _, timer := range el.timers {
		if timer.Running {
			timer.Running = false
			if stopChan, ok := el.timerStops[timer.ID]; ok {
				close(stopChan)
			}
		}
	}
}

// ActiveTimerCount returns the number of running timers
func (el *EventLoop) ActiveTimerCount() int {
	el.mu.Lock()
	defer el.mu.Unlock()

	count := 0
	for _, timer := range el.timers {
		if timer.Running && !timer.Cancelled {
			count++
		}
	}
	return count
}

// Reset clears all timers (for testing)
func (el *EventLoop) Reset() {
	el.mu.Lock()
	defer el.mu.Unlock()

	for _, timer := range el.timers {
		if timer.Running {
			if stopChan, ok := el.timerStops[timer.ID]; ok {
				close(stopChan)
			}
		}
	}
	el.timers = make(map[int]*TimerValue)
	el.timerStops = make(map[int]chan struct{})
	el.running = false
}
