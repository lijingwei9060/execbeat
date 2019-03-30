// Config is put into a different package to prevent cyclic imports in case
// it is needed in several locations

package config

import (
	"github.com/lijingwei9060/execbeat/utils/schedulecommand"
)

type Config struct {
	Commands []schedulecommand.ScheduleCommandConfig `config:"commands" validate:"required"`
}

var DefaultConfig = Config{}
