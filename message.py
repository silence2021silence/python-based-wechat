from flask import abort, request
import hashlib
import config
from WXBizMsgCrypt import WXBizMsgCrypt
from xml.dom.minidom import parseString
import time
import loger
# 定义时间戳变量
time_stamp = int(time.time())


def receive_message(signature, timestamp, nonce):
    if signature and timestamp and nonce:
        # 加进同一列表
        list1 = [config.token, timestamp, nonce]
        # 排序
        list1.sort()
        # 列表转字符串
        str1 = "".join(list1)
        # 生成SHA1值
        sha1_str = hashlib.sha1(str1.encode("UTF-8")).hexdigest()
        # 比对
        # 若一致
        if signature == sha1_str:
            # 若请求方式为GET
            # 则认定为第一次配置服务器而发来的请求
            if request.method == "GET":
                # 从json中获取参数
                echostr = request.args.get("echostr")
                # 若存在此参数
                if echostr:
                    # 直接返回
                    return echostr
                # 若不存在此参数
                else:
                    # 返回 错误请求
                    abort(400)
                    print("No echostr.")
            # 若请求方式为POST
            # 则认定为公众号来消息了
            elif request.method == "POST":
                # 从json中获取参数
                msg_signature = request.args.get("msg_signature")
                # 获取POST过来的bytes格式数据
                encrypted_bytes = request.data
                # 若存在
                if encrypted_bytes:
                    # 微信官方提供的SDK解密
                    keys = WXBizMsgCrypt(config.token, config.encodingaeskey, config.appid)
                    decrypt_ierror, decrypted_bytes = keys.DecryptMsg(encrypted_bytes, msg_signature, timestamp, nonce)
                    # 若解密错误码为0
                    # 则认定为解密成功
                    if decrypt_ierror == 0:
                        # 解析XML
                        dom_data = parseString(decrypted_bytes).documentElement
                        # 从XML中获取参数
                        # 获取消息类型
                        msg_type = dom_data.getElementsByTagName("MsgType")[0].childNodes[0].data
                        # 若消息类型为text文字
                        if msg_type == "text":
                            # 从XML中获取以下参数
                            to_user_name = dom_data.getElementsByTagName("ToUserName")[0].childNodes[0].data
                            from_user_name = dom_data.getElementsByTagName("FromUserName")[0].childNodes[0].data
                            create_time = dom_data.getElementsByTagName("CreateTime")[0].childNodes[0].data
                            content = dom_data.getElementsByTagName("Content")[0].childNodes[0].data
                            msg_id = dom_data.getElementsByTagName("MsgId")[0].childNodes[0].data
                            # 写入Excel日志文件
                            loger.MessageLoger(msg_type, to_user_name, from_user_name, create_time, content, msg_id)
                            # 创建一个消息的XML模板用于被动回复
                            message_xml_model = """<xml>
                                                    <ToUserName><![CDATA[%s]]></ToUserName>
                                                    <FromUserName><![CDATA[%s]]></FromUserName>
                                                    <CreateTime>%d</CreateTime>
                                                    <MsgType><![CDATA[text]]></MsgType>
                                                    <Content><![CDATA[%s]]></Content>
                                                    </xml>"""
                            #
                            if content == "哈":
                                message_xml_1 = message_xml_model % (from_user_name, to_user_name, time_stamp, "嗨害嗨")
                                encrypt_ierror, encrypted_str = keys.EncryptMsg(message_xml_1, nonce)
                                if encrypt_ierror == 0:
                                    return encrypted_str.encode("UTF-8")
                                else:
                                    # 返回 错误请求
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
                            # 返回 错误请求
                            abort(400)
                            print("Other type message.")
                    else:
                        # 返回 错误请求
                        abort(400)
                        print("Decrypt_ierror:" + str(decrypt_ierror))
                else:
                    # 返回 错误请求
                    abort(400)
                    print("No encrypted_bytes.")
            else:
                # 返回 错误请求
                abort(400)
                print("No GET or POST.")
        else:
            # 返回 拒绝请求
            abort(403)
            print("signature != sha1_str.")
    else:
        # 返回 错误请求
        abort(400)
        print("No signature or timestamp or nonce.")
