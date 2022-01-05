# smtp2go-monitor
A small logging utility using the smtp2go api to pull activity logs for monitoring in ELK

A small python program utilizing api.smtp2go.com to pull periodically activity to feed into other logging systems. All program output is JSON lines making it simple to feed into a log analytics solution such as ELK stack or similar. There is also provided a Docker image to easily get up and running.
