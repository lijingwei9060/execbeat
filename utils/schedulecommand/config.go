package schedulecommand

import "time"

// ScheduleCommandConfig provides information about command
type ScheduleCommandConfig struct {
	Name      string            `config:"name" validate:"required"`
	Enabled   bool              `config:"enabled"` // 脚本是否启动
	Command   string            `config:"command" validate:"required"`
	Args      string            `config:"args"`
	Timeout   time.Duration     `config:"timeout"`                       // 脚本执行超时时间
	NameSpace string            `config:"namespace" validate:"required"` // 命名空间
	Separator string            `config:"separator"`                     // k,v 分割字符串，默认：
	DropError bool              `config:"droperror"`                     // 如果执行出错，是否接收返回数据，默认true
	Schedule  string            `config:"schedule" validate:"required"`
	Fields    map[string]string `config:"fields"`
}

type Config struct {
	Commands []ScheduleCommandConfig `config:"commands" validate:"required"`
}

var (
	DefaultTimeout   = 5 * time.Minute
	DefaultSeparator = ":"
)
