图形化界面的多进程代码统计工具
实现框架
1.find_all_code_file(file_queue, file_path, file_type=None)：统计文件个数
2.single_def single_file_code_line_count(file_queue, total_code_line_count, total_annotation_line_count, total_space_line_count)：统计单个文件中的代码行数，注释行数以及空行数
3.all_file_code_line_count：
  1.定义多进程函数，并将统计出来的带待统计的文件放入到队列中
  2.将单个文件代码统计函数作为任务函数
  3.启动多进程，并阻塞主进程
  4.返回统计结果，给图形界面展示
4.gui(file_queue):实现图形化的页面，统计文件的路径由页面输入，并输出统计结果到页面展示
