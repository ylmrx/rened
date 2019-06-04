# Rened

## meaning

René is a french idiotic mole.

A mole digs tunnel.

Rened is a daemon to handle tunnels.

## goal

I wanted a simple way to handle many ssh tunnels from a single file/daemon. And rely only on paramiko.

## usage

`rened.py [-v] config_file`

- If `config_file` is omitted, it will try to open `~/.rened.json`.
- `-v/--verbose` will switch to debug mode, for a surprising volume of mildly interesting logs.

## credits

This script is based on this demo from paramiko.

https://github.com/paramiko/paramiko/blob/master/demos/forward.py

## future (TODO)

- systemd user-script (so it start with your session)
- install script

## music

https://www.youtube.com/watch?v=24pUKRQt7fk

(yes, it's this bad.)
