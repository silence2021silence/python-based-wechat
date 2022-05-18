from flask import Flask, request, abort
from gevent import pywsgi
import hashlib
import config
from WXBizMsgCrypt import WXBizMsgCrypt
from xml.dom.minidom import parseString
import time
import loger

app = Flask(__name__)
app.debug = True


@app.route('/', methods=["GET", "POST"])
def index():
    signature = request.args.get("signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")
    if verify_signature(signature, timestamp, nonce) == 0:
        if request.method == "GET":
            return_echostr()
        elif request.method == "POST":
            decrypted_bytes = decryption(timestamp, nonce)
            msg_type = message_type(decrypted_bytes)
            to_user_name, from_user_name = xml_data(decrypted_bytes, msg_type)
            message_xml = send_text(from_user_name, to_user_name)
            encrypted_str = encryption(message_xml, nonce)
            return encrypted_str


def verify_signature(signature, timestamp, nonce):
    if signature and timestamp and nonce:
        list1 = [config.token, timestamp, nonce]
        list1.sort()
        str1 = "".join(list1)
        sha1_str = hashlib.sha1(str1.encode("UTF-8")).hexdigest()
        if signature == sha1_str:
            return 0
        else:
            abort(403)


def return_echostr():
    echostr = request.args.get("echostr")
    if echostr:
        return echostr
    else:
        abort(400)


def decryption(timestamp, nonce):
    msg_signature = request.args.get("msg_signature")
    encrypted_bytes = request.data
    if encrypted_bytes:
        keys = WXBizMsgCrypt(config.token, config.encodingaeskey, config.appid)
        decrypt_ierror, decrypted_bytes = keys.DecryptMsg(encrypted_bytes, msg_signature, timestamp, nonce)
        if decrypt_ierror == 0:
            return decrypted_bytes


def encryption(message_xml, nonce):
    keys = WXBizMsgCrypt(config.token, config.encodingaeskey, config.appid)
    encrypt_ierror, encrypted_str = keys.EncryptMsg(message_xml, nonce)
    if encrypt_ierror == 0:
        return encrypted_str.encode("UTF-8")


def message_type(decrypted_bytes):
    dom_data = parseString(decrypted_bytes).documentElement
    msg_type = dom_data.getElementsByTagName("MsgType")[0].childNodes[0].data
    return msg_type


def xml_data(decrypted_bytes, msg_type):
    dom_data = parseString(decrypted_bytes).documentElement
    to_user_name = dom_data.getElementsByTagName("ToUserName")[0].childNodes[0].data
    from_user_name = dom_data.getElementsByTagName("FromUserName")[0].childNodes[0].data
    create_time = dom_data.getElementsByTagName("CreateTime")[0].childNodes[0].data
    msg_id = dom_data.getElementsByTagName("MsgId")[0].childNodes[0].data
    # msg_data_id = dom_data.getElementsByTagName("MsgDataId")[0].childNodes[0].data
    # id_x = dom_data.getElementsByTagName("Idx")[0].childNodes[0].data
    if msg_type == "text":
        content = dom_data.getElementsByTagName("Content")[0].childNodes[0].data
        loger.MessageLoger("text", to_user_name, from_user_name, create_time, content, msg_id)
    if msg_type == "image":
        pic_url = dom_data.getElementsByTagName("PicUrl")[0].childNodes[0].data
        media_id = dom_data.getElementsByTagName("MediaId")[0].childNodes[0].data
    if msg_type == "voice":
        media_id = dom_data.getElementsByTagName("MediaId")[0].childNodes[0].data
        format_ = dom_data.getElementsByTagName("Format")[0].childNodes[0].data
    if msg_type == "video":
        media_id = dom_data.getElementsByTagName("MediaId")[0].childNodes[0].data
        thumb_media_id = dom_data.getElementsByTagName("ThumbMediaId")[0].childNodes[0].data
    if msg_type == "shortvideo":
        media_id = dom_data.getElementsByTagName("MediaId")[0].childNodes[0].data
        thumb_media_id = dom_data.getElementsByTagName("ThumbMediaId")[0].childNodes[0].data
    if msg_type == "location":
        location_x = dom_data.getElementsByTagName("Location_X")[0].childNodes[0].data
        location_y = dom_data.getElementsByTagName("Location_Y")[0].childNodes[0].data
        scale = dom_data.getElementsByTagName("Scale")[0].childNodes[0].data
        label = dom_data.getElementsByTagName("Label")[0].childNodes[0].data
    return to_user_name, from_user_name


def send_text(to_user_name, from_user_name):
    message_xml_model = """<xml>
                            <ToUserName><![CDATA[%s]]></ToUserName>
                            <FromUserName><![CDATA[%s]]></FromUserName>
                            <CreateTime>%d</CreateTime>
                            <MsgType><![CDATA[text]]></MsgType>
                            <Content><![CDATA[%s]]></Content>
                            </xml>"""
    message_xml = message_xml_model % (to_user_name, from_user_name, int(time.time()), "嗨害嗨www.zhangkelan.com")
    return message_xml


def send_image():
    pass


def send_voice():
    pass


def send_video():
    pass


def send_shortvideo():
    pass


def send_location():
    pass


def send_link():
    pass


if __name__ == '__main__':
    # 此配置解决WSGI报错问题
    server = pywsgi.WSGIServer(("0.0.0.0", 5000), app)
    server.serve_forever()
    # app.run(host="0.0.0.0", port=5000, debug=True)
