# open-stream

python tool used to extract an m3u8 playlist and start vlc using the URLS and the token.

This tools will use chrome and vlc to open the stream.

## How to
first setup the env as in 
`$ setup.sh`

Find an event, copy the URL and start the view.sh as
`$./view.sh "URL"`

This will start the python proxy that will handle the parsing of the url and the renewal of the token
and start the vlc process.

At the end, to stop the process and the proxy use
`$./stop.sh`

## Other tool

Find an event and use the tool as in 
`$ ./start.sh your-url-here`

## Disclaimer 
This tool is for research purpose only. Use it to learn and only in appropriated ways.

I take no responsiblity for the usage of the tool or eventual problem/issues/damages for the code contained in this repository.
Understand what you are doing.


