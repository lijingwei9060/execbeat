package cron

// ScheduleCommandConfig provides config for cron
type ScheduleCommandConfig struct {
	Schedule string            `config:"schedule" validate:"required"`
	Fields   map[string]string `config:"fields"`
}

type Config struct {
	Commands []ScheduleCommandConfig `config:"commands" validate:"required"`
}

var (
	DefaultConfig = Config{}
)
