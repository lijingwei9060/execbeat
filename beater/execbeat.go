package beater

import (
	"fmt"

	"github.com/lijingwei9060/execbeat/utils/schedulecommand"

	"github.com/elastic/beats/libbeat/beat"
	"github.com/elastic/beats/libbeat/common"
	"github.com/elastic/beats/libbeat/logp"

	"github.com/lijingwei9060/execbeat/config"
)

// Execbeat configuration.
type Execbeat struct {
	done   chan struct{}
	config config.Config
	client beat.Client
}

// New creates an instance of execbeat.
func New(b *beat.Beat, cfg *common.Config) (beat.Beater, error) {
	c := config.DefaultConfig
	if err := cfg.Unpack(&c); err != nil {
		return nil, fmt.Errorf("Error reading config file: %v", err)
	}

	bt := &Execbeat{
		done:   make(chan struct{}),
		config: c,
	}
	return bt, nil
}

// Run starts execbeat.
func (bt *Execbeat) Run(b *beat.Beat) error {
	logp.Info("execbeat is running! Hit CTRL-C to stop it.")

	var err error
	bt.client, err = b.Publisher.Connect()
	if err != nil {
		return err
	}

	for _, c := range bt.config.Commands {
		if !c.Enabled {
			continue // 如果没有启动，则跳过
		}
		sc, _ := schedulecommand.New(c, bt.client)
		logp.Info("start command %v at interval %v", c.Name, c.Schedule)
		go sc.Run()
	}

	for {
		select {
		case <-bt.done:
			return nil
		}
	}
}

// Stop stops execbeat.
func (bt *Execbeat) Stop() {
	bt.client.Close()
	close(bt.done)
}
