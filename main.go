package main

import (
	"os"

	"github.com/lijingwei9060/execbeat/cmd"

	_ "github.com/lijingwei9060/execbeat/include"
)

func main() {
	if err := cmd.RootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}
