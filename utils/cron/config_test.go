package cron

// import (
// 	"path/filepath"
// 	"testing"
// 	"time"

// 	"github.com/elastic/beats/libbeat/cfgfile"
// 	"github.com/stretchr/testify/assert"
// )

// func TestRead(t *testing.T) {
// 	absPath, err := filepath.Abs("../../tests/files/")

// 	assert.NotNil(t, absPath)
// 	assert.Nil(t, err)

// 	config := &Config{}

// 	err = cfgfile.Read(config, absPath+"/config.yml")
// 	t.Log(config)
// 	assert.Nil(t, err)

// 	commands := config.Commands
// 	assert.Equal(t, 2, len(commands))

// 	assert.Equal(t, "MegaRAID", commands[0].Name)
// 	assert.Equal(t, "MegaCli", commands[0].Command)
// 	assert.Equal(t, "-adpAll -aAll", commands[0].Args)
// 	assert.Equal(t, "@every 30s", commands[0].Schedule)
// 	assert.Equal(t, 2, len(commands[0].Fields))
// 	assert.Equal(t, true, commands[0].DropError)
// 	assert.Equal(t, "hw.raid", commands[0].NameSpace)
// 	assert.Equal(t, ":", commands[0].Separator)
// 	assert.Equal(t, 5*time.Minute, commands[0].Timeout)

// 	// assert.Equal(t, "echo2", commands[1].Name)
// 	// assert.Equal(t, "Hello World", commands[1].Args)
// 	// assert.Equal(t, "@every 2m", commands[1].Schedule)
// 	// assert.Equal(t, 0, len(commands[1].Fields))
// 	// assert.Equal(t, false, commands[1].DropError)
// 	// assert.Equal(t, "system.hw", commands[1].NameSpace)
// 	// assert.Equal(t, ":", commands[1].Separator)
// 	// assert.Equal(t, 5*time.Minute, commands[1].Timeout)

// }
