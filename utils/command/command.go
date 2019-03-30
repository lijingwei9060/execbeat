package command

import (
	"bytes"
	"context"
	"fmt"
	"os"
	"os/exec"
	"strings"
	"syscall"
	"time"
)

var (
	// ErrNoCommand 命令不存在
	ErrNoCommand = fmt.Errorf("no command error")
)

// TimeOutCommand 可以执行command，定时超时
type TimeOutCommand struct {
	command string
	args    string
	timeout time.Duration
}

// New 根据参数创建一个TimeOutCommand执行期
func New(c string, a string, t time.Duration) (*TimeOutCommand, error) {
	if c == "" {
		return nil, ErrNoCommand
	}

	command := &TimeOutCommand{
		command: c,
		args:    a,
		timeout: t,
	}
	return command, nil
}

// Run 执行命令返回 out,error,exitcode
func (tc *TimeOutCommand) Run() (string, string, int) {
	var err error
	var stdout bytes.Buffer
	var stderr bytes.Buffer
	var waitStatus syscall.WaitStatus
	var exitCode int = 0

	ctx, cancel := context.WithTimeout(context.Background(), tc.timeout)
	defer cancel() // The cancel should be deferred so resources are cleaned up

	// Create the command with our context
	var cmd *exec.Cmd
	if tc.args != "" {
		cmd = exec.CommandContext(ctx, tc.command, strings.Split(tc.args, " ")...)
	} else {
		cmd = exec.CommandContext(ctx, tc.command)
	}

	cmd.Env = append(os.Environ(), "lang=en_US.utf-8")
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	// run the command
	err = cmd.Run()
	fmt.Print(stderr.String())
	fmt.Print(stdout.String())
	fmt.Print(err)
	// Check the context error to see if the timeout was executed.
	// The error returned by cmd.CombinedOutput() will be OS specific based on what
	// happens when a process is killed.
	if ctx.Err() == context.DeadlineExceeded {
		exitCode = 127
		stderr.Write([]byte(context.DeadlineExceeded.Error()))

	}

	if err != nil {
		if exitError, ok := err.(*exec.ExitError); ok {
			waitStatus = exitError.Sys().(syscall.WaitStatus)
			exitCode = waitStatus.ExitStatus()
		}
	}
	// If there's no context error, we know the command completed (or errored).
	return stdout.String(), stderr.String(), exitCode
}
