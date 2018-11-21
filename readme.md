# What is it

This is code I made for testwarez preso about fuzzing Rest APIs. 

# How to run it

## vulnerable_server

First start vulnerable server or other target you want to break like http-server (brew install http-server).
```
pip install Flask-API
pip install Flask
PORT=5000 python vulnerable_server.py
```

## start fuzzing

Each mainX.py contains more and more complex scenario of usage.

```
pip install -r requirements.txt
python main<X>.py
```

Examine http://127.0.0.1:26000/ for report. When finished, ctrl-c process. 

More docs:

1) [Kitty](https://kitty.readthedocs.io/en/latest/)
2) [Katnip](https://katnip.readthedocs.io)

