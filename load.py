# -*- coding: utf-8 -*-
# @Time    : 2019/4/15 12:48
# @Author  : 郭建宇
# @Email   : 276381225@qq.com
# @File    : 2.py
# @Software: PyCharm
import os
import subprocess
def run_cmd(cmd):  # 执行youtube下载视频的命令
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    child.wait()
    Returncode = child.stdout.read()
    return Returncode

def load_images():
    dirs = os.listdir("/root/guojianyu/BaseImage_ARM")
    a = 0
    for file_name in dirs:
        if os.path.splitext(file_name)[1] == '.tar':
            print(file_name)
            a+=1
            run_cmd("docker load -i %s"%(file_name))

    print (a)

def update_name():
    a = open("images_info.txt","r")
    content =a.readlines()
    for item in content:
        item  = item.split(":")
        id = item[0]
        name = item[1]+":"+item[2].replace("\n","")
        cmd = "docker tag %s  %s"%(id,name)
        run_cmd(cmd)
        print (id)
        print (name)
    pass

if __name__ == "__main__":
    update_name()