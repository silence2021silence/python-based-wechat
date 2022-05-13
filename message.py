from flask import abort, request
import hashlib
import config
from WXBizMsgCrypt import WXBizMsgCrypt
from xml.dom.minidom import parseString
import time

time_stamp = int(time.time())


def receive_message(signature, timestamp, nonce):
    if signature and timestamp and nonce:
        list1 = [config.token, timestamp, nonce]
        list1.sort()
        str1 = "".join(list1)
        sha1_str = hashlib.sha1(str1.encode("UTF-8")).hexdigest()

        if signature == sha1_str:
            if request.method == "GET":
                echostr = request.args.get("echostr")
                if echostr:
                    return echostr
                else:
                    abort(400)
                    print("No echostr.")

            elif request.method == "POST":
                msg_signature = request.args.get("msg_signature")
                encrypted_bytes = request.data
                if encrypted_bytes:
                    keys = WXBizMsgCrypt(config.token, config.encodingaeskey, config.appid)
                    decrypt_ierror, decrypted_bytes = keys.DecryptMsg(encrypted_bytes, msg_signature, timestamp, nonce)
                    if decrypt_ierror == 0:
                        dom_data = parseString(decrypted_bytes).documentElement
                        msg_type = dom_data.getElementsByTagName("MsgType")[0].childNodes[0].data
                        if msg_type == "text":
                            to_user_name = dom_data.getElementsByTagName("ToUserName")[0].childNodes[0].data
                            from_user_name = dom_data.getElementsByTagName("FromUserName")[0].childNodes[0].data
                            create_time = dom_data.getElementsByTagName("CreateTime")[0].childNodes[0].data
                            content = dom_data.getElementsByTagName("Content")[0].childNodes[0].data
                            msg_id = dom_data.getElementsByTagName("MsgId")[0].childNodes[0].data
                            message_xml_model = """<xml>
                                                    <ToUserName><![CDATA[%s]]></ToUserName>
                                                    <FromUserName><![CDATA[%s]]></FromUserName>
                                                    <CreateTime>%d</CreateTime>
                                                    <MsgType><![CDATA[text]]></MsgType>
                                                    <Content><![CDATA[%s]]></Content>
                                                    </xml>"""
                            if content == "哈":
                                message_xml_1 = message_xml_model % (from_user_name, to_user_name, time_stamp, "嗨害嗨")
                                encrypt_ierror, encrypted_str = keys.EncryptMsg(message_xml_1, nonce)
                                if encrypt_ierror == 0:
                                    return encrypted_str.encode("UTF-8")
                                else:
                                    abort(400)
                                    print("Encrypt_ierror:" + str(encrypt_ierror))
                            else:
                                message_xml_2 = message_xml_model % (from_user_name, to_user_name, time_stamp, content)
                                return message_xml_2
                        elif msg_type == "image":
                            pass
                        elif msg_type == "voice":
                            pass
                        elif msg_type == "video":
                            pass
                        elif msg_type == "shortvideo":
                            pass
                        elif msg_type == "location":
                            pass
                        elif msg_type == "link":
                            pass
                        else:
                            abort(400)
                            print("Other type message.")
                    else:
                        abort(400)
                        print("Decrypt_ierror:" + str(decrypt_ierror))
                else:
                    abort(400)
                    print("No encrypted_bytes.")
            else:
                abort(400)
                print("No GET or POST.")
        else:
            abort(403)
            print("signature != sha1_str.")
    else:
        abort(400)
        print("No signature or timestamp or nonce.")
