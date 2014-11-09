A logging bot for XMPP chat rooms.

# What?
* XMPP Log bot
* Search interface (with whoosh and flask)
* Log to text files

# Install

    pip install logbot

# Running

You can run logbot with arguments passed on the command line, or you can use a
config file.

## Passing args on the command line

    logbot \
        --host chat.looney.org \
        --user logbot@chat.looney.org \
        --passwd  S3cr3t \
        yada@conference.looney.org

## Passing args through a config file

logbot checks for config in the following order, with command line args having
the highest priority.

  - /etc/logbot.ini
  - ~/.logbot/config
  - command line args

Using a config file allows you to keep the account password hidden from the
process list when not entering the password dynamically.

The accepted config items, and their defaults, are any combination of the following:

    [logbot]
    user =
    passwd =
    host = localhost
    port = 5222
    tls = true
    timezone = None
    rooms =

Multiple rooms may be passed as a space separated list.  Any rooms passed in the config files will be appended to rooms passed on the command line.

## Web interface

By default the web interface is available at [http://localhost:5000](http://localhost:5000)

The listening address and port can be overridden in the config by adding a
section as follows:

    [httpd]
    listen_address = 10.9.8.7
    listen_port    = 9000

# Bugs

Version 0.3.0 changed search schema. Please run `utils/upgrade_03.py` to update
the schema.

# Contact
Miki Tebeka <miki.tebeka@gmail.com>

Bugs go [here](https://bitbucket.org/tebeka/logbot/issues)

<!---
vim: spell
-->
