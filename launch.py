from flask import Flask, request, abort
from gevent import pywsgi
import hashlib

flask_app = Flask(__name__)


@flask_app.route('/', methods=["GET", "POST"])
def home():
  # 微信服务器发来的三个get参数
  signature = request.args.get("signature")
  timestamp = request.args.get("timestamp")
  nonce = request.args.get("nonce")
  # 公众号后台自己填写的token
  token = "[此处替换Token]"
  # 加进同一个列表里
  list1 = [token, timestamp, nonce]
  # 排序
  list1.sort()
  # 把列表转换成字符串
  str1 = "".join(list1)
  # 生成sha1值
  sha1_str = hashlib.sha1(str1.encode("utf-8")).hexdigest()
  # 与signature参数比对
  # 若不一致
  if signature != sha1_str:
      # 被认定为非微信服务器发来的get请求
      # 返回403拒接请求
      abort(403)
  # 若一致
  else:
      # 判断
      # 若为get请求则认定为开发者第一次配置服务器
      if request.method == "GET":
          # 定义echostr参数
          echostr = request.args.get("echostr")
          # 判断get参数中是否含有echostr参数
          if echostr:
              # 若存在则按官方文档要求原样返回
              return echostr
          # 若不存在则返回400错误请求
          else:
              abort(400)


if __name__ == '__main__':
  # 此配置解决WSGI报错问题
  server = pywsgi.WSGIServer(('0.0.0.0', 5000), flask_app)
  server.serve_forever()
  
