package schedulecommand

import (
	"bufio"
	"io"
	"strings"
	"time"

	"github.com/elastic/beats/libbeat/logp"

	"github.com/elastic/beats/libbeat/beat"
	"github.com/elastic/beats/libbeat/common"
	"github.com/lijingwei9060/execbeat/utils/command"
	"github.com/robfig/cron"
)

// ScheduleCommand 定期调度的命令服务
type ScheduleCommand struct {
	config ScheduleCommandConfig
	client beat.Client
}

// New 根据config创建一个ScheduleCommand
func New(c ScheduleCommandConfig, client beat.Client) (*ScheduleCommand, error) {
	sc := &ScheduleCommand{
		config: c,
		client: client,
	}
	return sc, nil
}

// Run 执行command
func (sc *ScheduleCommand) Run() {
	// 设置默认参数
	if sc.config.Timeout == 0 {
		sc.config.Timeout = DefaultTimeout
	}

	if sc.config.Separator == "" {
		sc.config.Separator = DefaultSeparator
	}

	cron := cron.New()
	cron.AddFunc(sc.config.Schedule, func() { sc.run() })
	cron.Start()

}

// run 执行command
func (sc *ScheduleCommand) run() {
	cmd, _ := command.New(sc.config.Command, sc.config.Args, sc.config.Timeout)
	now := time.Now()
	out, err, ec := cmd.Run()
	tc := time.Now().Sub(now) //执行时间

	if err != "" || ec != 0 { //执行脚本有错误
		e := beat.Event{
			Timestamp: time.Now(),
			Fields: common.MapStr{
				"command":  sc.config.Command,
				"exitcode": ec,
				"error":    err,
				"duration": tc,
			},
		}
		sc.client.Publish(e) //把执行错误信息发出去
		return               // 如果有错误就不发有问题的event
	}

	logp.Info(out)
	logp.Info(err)
	s := strings.NewReader(out)
	br := bufio.NewReader(s)
	fields := common.MapStr{
		"command":  sc.config.Command,
		"duration": tc,
	}
	for {
		line, err := br.ReadString('\n')
		if err != nil || io.EOF == err {
			break
		}
		f := strings.Split(line, sc.config.Separator)
		if len(f) != 2 {

			continue
		}
		fields.Update(common.MapStr{strings.TrimSpace(f[0]): strings.TrimSpace(f[1])})
	}

	e := beat.Event{
		Timestamp: time.Now(),
	}

	for k, v := range sc.config.Fields {
		fields.Update(common.MapStr{k: v})
	}

	if sc.config.NameSpace != "" {
		e.Fields = common.MapStr{sc.config.NameSpace: fields}
	} else {
		e.Fields = fields
	}

	sc.client.Publish(e)
}
