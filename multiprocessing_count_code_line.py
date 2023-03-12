# -*- coding: utf-8 -*-
"""
@Time ： 2023/3/12 14:32
@Auth ： 胡英俊(请叫我英俊)
@File ：multiprocessing_count_code_line.py
@IDE ：PyCharm
@Motto：一身正气
"""

import os
import chardet
import tkinter
import multiprocessing
import time


# 统计指定目录下代码文件，并添加到队列中，等待统计计算
def find_all_code_file(file_queue, file_path, file_type=None):
    # 判断目录下的文件是否为需要进行统计的代码文件
    if file_type is None:
        file_type = [".py", ".cpp", ".java", ".c", ".h", ".php", ".asp"]
    # path目录为单个文件时
    if os.path.isfile(file_path):
        if os.path.splitext(file_path) in file_type:
            file_queue.put(file_path)
        else:
            return "文件格式错误，无法统计，请重新输入"
    else:
        for root, dirs, files in os.walk(file_path):
            for file in files:
                if os.path.splitext(file)[1] in file_type:
                    file_queue.put(os.path.join(root, file))
    return file_queue


# 统计单个文件中的代码行数：总行数，代码行数，空白行以及注释行
def single_file_code_line_count(file_queue, total_code_line_count, total_annotation_line_count, total_space_line_count):
    while not file_queue.empty():
        file_path = file_queue.get()
        # 判断是否为多行注释的标识符号
        flag = True
        if not os.path.exists(file_path):
            return "file not exist"
        else:
            # 首先获取文件的编码
            with open(file_path, "rb") as fp:
                content = fp.read()
            file_chardet = chardet.detect(content)["encoding"]
            fp = open(file_path, encoding=file_chardet)
            for line in fp:
                # 判断是否多行注释，并进行处理
                if line.strip().startswith("'''") or line.strip().startswith('"""') or \
                        line.strip().endswith("'''") or line.strip().endswith('"""'):
                    # 如果标志位是false,修改为True，此段开始统计多行注释，如果标志位为TRUE，修改为False,此段多行注释统计结束
                    if flag is not True:
                        flag = True
                    else:
                        flag = False
                    total_annotation_line_count.value += 1
                elif line.strip().startswith("/*"):  # 开头为多行注释的符号时，修改标志位True
                    flag = True
                elif line.strip().endswith("/*"):  # 结尾是多行注释时，修改标志位
                    flag = False
                else:
                    # 通过标志位，是否跳出多行注释
                    if not flag:
                        # 判断空行
                        if line.strip() == "":
                            total_space_line_count.value += 1  # 统计空行
                            continue
                        # 单行注释需要区分是否为文件编码声明
                        elif line.strip().startswith("#") or line.strip().startswith("//"):
                            # 编辑声明
                            if line.strip().startswith("# encoding") or line.strip().startswith("#coding") \
                                    or line.strip().startswith("# -*-"):
                                total_code_line_count.value += 1
                            # 不是编码声明的情况则为单行注释
                            else:
                                total_annotation_line_count.value += 1
                        # 不是空行，不是单行注释时，其余的则为代码行
                        else:
                            total_code_line_count.value += 1
                    # 多行注释的标志位仍然为True,则此时的行仍然为注释行
                    else:
                        total_annotation_line_count.value += 1
            fp.close() # 文件内容统计结束，关闭文件，防止句柄泄露
            return total_code_line_count, total_annotation_line_count, total_space_line_count


# 使用多进程的方式进行统计操作
def all_file_code_line_count(file_queue, file_path, file_type):
    # 记录开始时间
    start_time = time.time()
    file_queue = find_all_code_file(file_queue, file_path, file_type)
    # 有效的代码文件数量
    total_file_count = file_queue.qsize()
    # 有效的代码行数量
    total_code_line_count = multiprocessing.Value("i", 0)
    # 总的注释行数量
    total_annotation_line_count = multiprocessing.Value("i", 0)
    # 总的空行数量
    total_space_line_count = multiprocessing.Value("i", 0)
    # 获取当前计算机的cpu核数
    cpu_num = multiprocessing.cpu_count()
    process_list = [multiprocessing.Process(target=single_file_code_line_count,args=(file_queue, total_code_line_count, total_annotation_line_count, total_space_line_count)) for i in range(cpu_num)]

    for p in process_list:
        p.start()
    for p in process_list:
        p.join()
    end_time = time.time()
    speed_time = end_time-start_time
    return total_file_count, total_code_line_count.value, total_annotation_line_count.value, total_space_line_count.value, speed_time


# GUI: 图形化代码统计工具
def gui(file_queue, file_type=None):

    # 创建主窗口
    window = tkinter.Tk()

    # 设置主窗口的标题
    window.title("代码统计工具")
    # 设置主窗口大小(长*宽)
    window.geometry("500x300")

    # label部件：界面提示语
    # 在主窗口上设置标签（显示文本）
    l1 = tkinter.Label(window, text="请输入需要统计的目录或者文件")
    # 放置标签
    l1.pack() # Label内容content区域放置位置，自动调节尺寸

    # Entry部件：单行文本输入
    e = tkinter.Entry(window, bd=5, width=50)
    e.pack()

    # 定义按钮Button实践的处理函数
    def button_click():
        file_path = e.get()
        result = all_file_code_line_count(file_queue, file_path, file_type)
        # 如果返回的是异常结果
        if isinstance(result, str):
            # 使用configure实现实时刷新数据
            l2.configure(text=result)
        # 返回数据正常
        else:
            code_file_count = result[0]
            code_line_count = result[1]
            annotation_count = result[2]
            space_line = result[3]
            time_speed= result[4]
            l2.configure(text="文件总数：{}\n代码行总数：{}\n注释行总数：{}\n空行总数：{}\n总耗时：{}秒\n".format(code_file_count, code_line_count, annotation_count,space_line, time_speed))

    # Button部件：按钮
    b = tkinter.Button(window, text="提交", command=button_click)
    b.pack()

    # 展示显示结果
    l2 = tkinter.Label(window,text="", width=200, height=10)
    l2.pack()

    # 主窗口循环显示
    window.mainloop()



if __name__ == "__main__":
    file_queue = multiprocessing.Queue()
    gui(file_queue)




