# #!/usr/bin/env python
# # -*- coding: UTF-8 -*-
#
# from selenium import webdriver
# import time
# import re
# import commands
# import os
# import shutil
# import xlrd
# import logging
# import subprocess
# import datetime
# from datetime import datetime
# from bs4 import BeautifulSoup
# from selenium.webdriver.support.ui import WebDriverWait
# # 定义 Jira 相关信息
# jira_url = "https://sharp-smart-mobile-comm.atlassian.net/"
# jira_issue_base_url = "https://sharp-smart-mobile-comm.atlassian.net/browse/"
# jira_doc_base_url = "https://sharp-smart-mobile-comm.atlassian.net/si/jira.issueviews:issue-word/"
# # 定义 Gerrit 相关信息
# gerrit_addresses = {
#     '10.24.71.180': 'https://secure.jp.sharp/android_review/gerrit',
#     '10.24.71.91': 'http://10.24.71.91/gerrit',
#     '10.230.1.88': 'http://10.230.1.88'
# }
#
# #flag 若只下载doc文件，更改值为False
# dld_gerrit_zip_flg = True
# #dld_gerrit_zip_flg = False
#
# # 删除相同的 Gerrit ID
# def jsw_gerrit_delete_same(id_list):
#     return list(set(id_list))
# # 设置 Firefox
# def jsw_use_firefox_default_profile(download_path, profile):
#     profile = webdriver.FirefoxProfile(profile)  # 加载配置文件
#     profile.set_preference('browser.download.dir', download_path)  # 指定文件下载路径
#     profile.set_preference('browser.download.folderList', 2)  # 文件下载方式 0-桌面 1-浏览器默认路径 2-指定路径
#     profile.set_preference('browser.download.manager.showWhenStarting', False)  # 开始下载时是否显示下载管理器(不起作用)
#     profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip, application/pdf, application/msword")  # 设置无需认可即可下载的文件格式
#     return profile
#
# # 重命名 zip 文件
# def jsw_rename_zip(r_id, num, jira_id, source_dir, download_path):
#     # 生成格式化的编号，如 01, 02 等
#     formatted_num = str(num).zfill(2)
#     re_name = jira_id.strip() + "-" + formatted_num + ".zip"
#     list = os.listdir(download_path)
#     for i in range(0, len(list)):
#         path = os.path.join(download_path, list[i])
#         if os.path.isfile(path):
#             if os.path.exists(os.path.join(source_dir, re_name)):
#                 os.unlink(path)
#                 print('Delete existing files')
#             else:
#                 shutil.move(path, os.path.join(source_dir, re_name))
#                 print('The file has been copied')
#     time.sleep(2)
#
# #Search gerrit link
# def jsw_find_gerrit(browser):
#     gerrit_list_p = []
#     gerrit_list_q = []
#     gerrit_list_ep2 = []
#     for link in browser.find_elements_by_xpath("//*[@href]"):
#         gerrit_str = link.get_attribute('href')
#         #find gerrit link
#         #print gerrit_str
#         ret_ep2 = gerrit_str.find('/#/c/') #查找关键字符
#         ret_q = gerrit_str.find('gerrit/')
#         ret_p = gerrit_str.find('gerrit/#/c/')
#
#         if ret_ep2 > 0 and gerrit_str.find('gerrit') == -1:
#             print 'ret_ep2'
#             print  (gerrit_str)
#             logger.info(gerrit_str)
#             # find gerrit id
#             ss = re.findall(r'\d+',gerrit_str)
#             #print ss
#             #if len(ss[0]) < 10 and int(ss[0]) >300000:
#             for i in ss:
#                 if 4 < len(i) < 10:
#                     gerrit_list_ep2.append(i)
#             else:
#                 pass
#         if ret_q > 0:
#             print 'ret_q'
#             print  (gerrit_str)
#             logger.info(gerrit_str)
#             # find gerrit id
#             ss = re.findall(r'\d+',gerrit_str)
#             #print ss
#             #if len(ss[0]) < 10 and int(ss[0]) >300000:
#             for i in ss:
#                 if 5< len(i) < 10:
#                     gerrit_list_q.append(i)
#             else:
#                 pass
#         if ret_p > 0:
#             print 'ret_p'
#             print  (gerrit_str)
#             logger.info(gerrit_str)
#             # find gerrit id
#             #ss = re.findall(r'(\w*[0-9]+)\w*',gerrit_str)
#             ss = re.findall(r'\d+',gerrit_str)
#             #print ss
#             #if len(ss[0]) < 10 and int(ss[0]) >300000:
#             if 4 < len(ss[0]) < 10:
#                 gerrit_list_p.append(ss[0])
#         else:
#             pass
#     return gerrit_list_p, gerrit_list_q, gerrit_list_ep2
#
#
# #Obtain date about creating ticket
# def find_ticket_date(browser):
#     date_list = []
#
#     for link in browser.find_elements_by_xpath("//*[@href]"):
#         date_str = link.get_attribute('href')
#         #print date_str
#         #ret = date_str.find('from')
#         link_date = re.findall('\d{4}-\d{2}-\d{2}',date_str)
#         if date_str.find('from') >=0 and link_date != []:
#             #print(date_str)
#             date_list.append(int(date_str.split('=')[-1].replace('-','')))
#     #print date_list
#     date_list.sort()
#     # 如果所有方法都失败，返回当前日期
#     #print("无法找到工单日期，使用当前日期作为替代")
#     now = datetime.now()
#     return int(now.strftime("%Y%m%d"))  # 返回整数格式 YYYYMMDD
#
#     ticket_date = now
#     return ticket_date
#
# #obtain commit date
# def find_commit_date(gerrit_id, name, gerrit_address):
#     commit_datelist = []
#     ssh_str = 'ssh -p 29418 '+name+'@'+gerrit_address+' gerrit query status:merged --current-patch-set --files change : '+gerrit_id+" |grep -i lastupdated |awk '{print $2}'"
#     #print ssh_str
#     commit_date_sum = commands.getoutput(ssh_str)#日期字符串
#     #commit_date_sum = os.system(ssh_str)
#     #pdb.set_trace()
#     #print commit_date_sum
#     commit_datelist = re.findall('\d{4}-\d{2}-\d{2}',commit_date_sum)#所有代码提交时间，例子中的代码第一个日期为最新
#     #print commit_datelist
#     try:
#         commit_date = int(commit_datelist[0].replace('-',''))
#     except:
#         print ("can't get "+commit_datelist)
#     return commit_date
#
# #download zip
# def jsw_gerrit_zip(browser, jira_id, gerrit_list, source_dir ,download_path, name, gerrit_address):
#     num = 0
#     #确定建票时间
#     ticket_date = find_ticket_date(browser)
#     logger.info(ticket_date)
#     print 'ticket_data=',ticket_date
#
#     for gerrit_id in gerrit_list:
#             ssh_str = "ssh -p 29418 "+name+"@"+gerrit_address+" gerrit query status:merged --format=TEXT --current-patch-set --files change:"+gerrit_id+" |grep 'revision:' |awk '{print $2}'"
#             # ssh gerrit query to get revision id
#             r_id = commands.getoutput(ssh_str) #commands模块用来调用linux shell命令，相当于直接在终端输入ssh_str,得到commit ID
#             #print r_id
#             #得到gerrit_id中每个代码的提交时间
#             logger.info(r_id)
#             ssh_str_status = 'ssh -p 29418 '+name+'@'+gerrit_address+' gerrit query status:merged --current-patch-set --files change : '+gerrit_id+' |grep -i "status"'
#             status = commands.getoutput(ssh_str_status)
#             ssh_str_project = 'ssh -p 29418 '+name+'@'+gerrit_address+' gerrit query status:merged --current-patch-set --files change : '+gerrit_id+" |grep -i project |awk '{print $2}'"
#             project = commands.getoutput(ssh_str_project)
#             if r_id != "":
#                 commit_date = find_commit_date(gerrit_id, name, gerrit_address)
#                 #print gerrit_id
#                 #print r_id
#                 print 'commit_date=',commit_date
#                 logger.info(commit_date)
#                 if commit_date-ticket_date <= 0:
#                     if gerrit_address == '10.230.1.88':
#                          dld_link = "http://10.230.1.88/changes/"+gerrit_id+"/revisions/"+r_id+"/patch?zip"
#                     elif gerrit_address == '10.24.71.180':
#                          dld_link = "https://secure.jp.sharp/android_review/gerrit/changes/"+gerrit_id+"/revisions/"+r_id+"/patch?zip"
#                     else:
#                          try:
#                             dld_link = "http://10.24.71.91/gerrit/changes/"+project.replace("/","%2F")+"~"+gerrit_id+"/revisions/"+r_id+"/patch?zip"
#                          except:
#                             continue
#
#                     # use js to open another window to download, because use brower.get, the firefox will block....
#                     js="window.open('"+dld_link+"')"
#                     print (js)
#                     try:
#                       browser.execute_script(js) #打开新窗口
#                     except:
#                       print("debug 226 ")
#                     # rename the zip
#                     num+=1
#                     time.sleep(2)
#                     jsw_rename_zip(r_id, num, jira_id, source_dir,download_path)
#
# # 下载 doc 文件
# def jsw_dld_doc(browser, jira_id, dir_path, download_path, name_fih, name_sharp):
#     doc_dir = download_path + '/' + dir_path + "/Investigation"
#     source_dir = download_path + '/' + dir_path + "/Source"
#     test_dir = download_path + '/' + dir_path + "/TestResult"
#     jsw_mkdir(doc_dir)
#     jsw_mkdir(source_dir)
#     jsw_mkdir(test_dir)
#     jira = jira_issue_base_url + jira_id
#     try:
#         browser.get(jira)
#         doc_url = jira_doc_base_url + jira_id + "/" + jira_id + ".doc"
#         js = "window.open('" + doc_url + "')"
#         browser.execute_script(js)
#         time.sleep(2)
#     except:
#         print("debug 250" + jira)
#         time.sleep(3)
#         time.sleep(2)
#
#     if dld_gerrit_zip_flg == True:
#         gerrit_list_p, gerrit_list_q, gerrit_list_ep2 = jsw_find_gerrit(browser)
#         if gerrit_list_p:
#             gerrit_list = jsw_gerrit_delete_same(gerrit_list_p)
#             jsw_gerrit_zip(browser, jira_id, gerrit_list_p, source_dir, download_path, name_sharp.upper(), gerrit_address='10.24.71.180')
#         else:
#             pass
#         if gerrit_list_q:
#             gerrit_list = jsw_gerrit_delete_same(gerrit_list_q)
#             jsw_gerrit_zip(browser, jira_id, gerrit_list_q, source_dir, download_path, name_sharp.lower(), gerrit_address='10.24.71.91')
#         else:
#             pass
#         if gerrit_list_ep2:
#             gerrit_list = jsw_gerrit_delete_same(gerrit_list_ep2)
#             jsw_gerrit_zip(browser, jira_id, gerrit_list_ep2, source_dir, download_path, name_fih, gerrit_address='10.230.1.88')
#         else:
#             pass
#     else:
#         pass
# # 创建文件夹
# def jsw_mkdir(path):
#     if not os.path.exists(path):
#         os.makedirs(path)
#         print(path + " created successfully")
#     else:
#         print(path + " directory exists")
# # 日志
# def get_logger():
#     logger = logging.getLogger(__name__)
#     logger.setLevel(level=logging.INFO)
#     log_path = default_name + 'logs'
#     jsw_mkdir(log_path)
#     os.chdir(log_path)
#     handler = logging.FileHandler(project_name + '.log', 'w')
#     handler.setLevel(logging.INFO)
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     handler.setFormatter(formatter)
#     handle_screen = logging.StreamHandler()
#     handle_screen.setLevel(logging.WARNING)
#     logger.addHandler(handler)
#     logger.addHandler(handle_screen)
#     return logger
# # 开始
# if __name__ == '__main__':
#     # 输入
#     default_name = raw_input('请输入下载路径：')
#     project_name = raw_input('请输入待处理文件名称：')
#     file_stype = raw_input('请输入待处理文件类型：')
#     profile = raw_input('请输入浏览器配置文件的绝对路径：')
#     name_login = raw_input('请输入 Gerrit 用户名：')
#     if default_name == '':
#         default_name = '/home/liwl/'
#     # 日志
#     logger = get_logger()
#     logger.info("[start]")
#     # 创建文件夹
#     dld_dir_base = os.path.join(default_name, project_name)
#     table_path = default_name + project_name + file_stype
#     dld_dir_base = dld_dir_base.strip()
#     jsw_mkdir(dld_dir_base)
#     if profile == '':
#         profile = '/home/liwl/.mozilla/firefox/9624lfot.default-release'
#     if name_login == '':
#         name_login = "sharp_audio_gr"
#     # 加载配置文件
#     prf = jsw_use_firefox_default_profile(dld_dir_base, profile)
#     # 启动浏览器
#     brser = webdriver.Firefox(prf)
#     # 打开表格
#     data = xlrd.open_workbook(table_path)
#     table = data.sheet_by_index(0)
#     nrows = table.nrows
#     # 从第二行（索引为 1）开始遍历，跳过表头
#     for i in range(1, nrows):
#         # 读取第一列数据作为 jira_id
#         jira_id = str(table.cell_value(i, 0)).strip()
#         # 读取第二列数据作为 folder_name
#         folder_name = str(table.cell_value(i, 1)).strip()
#         # 检查 jira_id 是否包含列表形式的数据
#         if '[' in jira_id and ']' in jira_id:
#             try:
#                 # 尝试解析列表形式的数据
#                 import ast
#                 parsed = ast.literal_eval(jira_id)
#                 if isinstance(parsed, list) and len(parsed) > 0:
#                     jira_id = str(parsed).strip()
#             except:
#                 pass
#         jsw_dld_doc(brser, jira_id, folder_name, dld_dir_base, "sharp_audio_gr", "lx19060027")
#     brser.close()
#     logger.info("[over]")
#
