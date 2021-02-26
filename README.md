# hindex

HTML indexer proof-of-concept

## usage

* With a Python virtualenv in hand, install requirements from `requirements.txt`.
* Run `python -m hindex -i input/jargon-4.4.7/html -o out/data` where `input/jargon-4.4.7/html` is a directory tree of HTML files.
  A structure of JSON files – one index file and several sub-index files – are created under `out/data`.
* Have a web server serve the `out/` directory. `live-server` or `serve` from npm work great, but `python -m http.server` should do in a pinch.
