import xlwt
import xlrd
from xlutils.copy import copy
import os
import datetime
# 日期时间变量
date_time = datetime.datetime.now()


class MessageLoger:
    def __init__(self, msg_type, to_user_name, from_user_name, create_time, content, msg_id):
        # 定义Excel文件路径
        self.xls_file = "log.xls"
        # 若此文件不存在
        if not os.path.exists(self.xls_file):
            # 调用 创建一个新的日志Excel文件 函数
            self.new_work_book()
            # 调用 追加写入Excel 函数
            self.write_work_book(msg_type, to_user_name, from_user_name, create_time, content, msg_id)
        else:
            # 若此文件存在则直接追加写入
            self.write_work_book(msg_type, to_user_name, from_user_name, create_time, content, msg_id)

    # 创建一个新的日志Excel文件
    def new_work_book(self):
        # 定义一个写入工作簿的对象
        work_book_writing = xlwt.Workbook(encoding="UTF-8")
        # 定义一个写入工作表的对象
        # cell_overwrite_ok=Flase 是否允许在一个单元格是否能多次写入
        work_sheet_writing = work_book_writing.add_sheet("Sheet1", cell_overwrite_ok=False)
        # 分别写入列头
        # write内第一个参数为行，第二个为列，第三个为写入值
        work_sheet_writing.write(0, 0, label="MsgType")
        work_sheet_writing.write(0, 1, label="ToUserName")
        work_sheet_writing.write(0, 2, label="FromUserName")
        work_sheet_writing.write(0, 3, label="CreateTime")
        work_sheet_writing.write(0, 4, label="Content")
        work_sheet_writing.write(0, 5, label="MsgId")
        work_sheet_writing.write(0, 6, label="DateTime")
        # 保存文件
        work_book_writing.save(self.xls_file)

    # 追加写入Excel
    def write_work_book(self, msg_type, to_user_name, from_user_name, create_time, content, msg_id):
        # 定义一个读取工作簿的对象
        # formatting_info=True 读取时保留原单元格格式
        work_book_reading = xlrd.open_workbook(self.xls_file, formatting_info=True)
        # 定义一个读取工作表的对象
        # sheet_by_index(0) 通过引索读取第一个工作表
        work_sheet_reading = work_book_reading.sheet_by_index(0)
        # 获取有效行数
        nrows = work_sheet_reading.nrows
        # 将工作簿对象拷贝，变成可写的workbook对象
        work_book_reading_copy = copy(work_book_reading)
        # 定义一个写入工作表的对象
        # sheet_by_index(0) 通过引索读取第一个工作表
        work_sheet_write = work_book_reading_copy.get_sheet(0)
        # 定义一个单元格格式的对象
        datetime_cell_style = xlwt.XFStyle()
        # 设置单元格显示格式
        datetime_cell_style.num_format_str = "yyyy-mm-dd hh:mm:ss"
        # 分别写入数据
        work_sheet_write.write(nrows, 0, label=msg_type)
        work_sheet_write.write(nrows, 1, label=to_user_name)
        work_sheet_write.write(nrows, 2, label=from_user_name)
        work_sheet_write.write(nrows, 3, label=create_time)
        work_sheet_write.write(nrows, 4, label=content)
        work_sheet_write.write(nrows, 5, label=msg_id)
        work_sheet_write.write(nrows, 6, label=date_time, style=datetime_cell_style)
        # 保存文件
        work_book_reading_copy.save(self.xls_file)
