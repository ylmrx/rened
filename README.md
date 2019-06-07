# Rened

## meaning

René is a french idiotic mole.

A mole digs tunnel.

Rened is a daemon to handle tunnels.

## goal

I wanted a simple way to handle many ssh tunnels from a single file/daemon. And rely only on paramiko.

## install

On ubuntu/debian, I think the best option is to rely on apt-provided python packages : 

```bash
sudo apt install python3-paramiko python3-click python3-colorlog
```

Then you can "autostart" it with your desktop session.

It will definitely work with pip and venvs, but will make the autostart things much sketchier.

```bash
pip install -r requirements.txt
```

## usage

`rened.py [-v] config_file`

- If `config_file` is omitted, it will try to open `~/.rened.json`. Use the provided `rened.conf.json` as a template
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
