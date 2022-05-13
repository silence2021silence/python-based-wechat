from flask import Flask, render_template, url_for, redirect, request, abort
from gevent import pywsgi
# from werkzeug.middleware.proxy_fix import ProxyFix
import message

app = Flask(__name__)
app.debug = True
# app.wsgi_app = ProxyFix(app.wsgi_app)


@app.route('/', methods=["GET", "POST"])
def home():
    signature = request.args.get("signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")
    return message.receive_message(signature, timestamp, nonce)


if __name__ == '__main__':
    server = pywsgi.WSGIServer(("0.0.0.0", 5000), app)
    server.serve_forever()
    # app.run(host="0.0.0.0", port=5000, debug=True)
