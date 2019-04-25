# -*- coding: utf-8 -*-
# @Time    : 2019/4/15 18:08
# @Author  : 郭建宇
# @Email   : 276381225@qq.com
# @File    : get_netspaces.py
# @Software: PyCharm
import paramiko
from functools import wraps
class SSHManager:
    def __init__(self, host, usr, passwd):
        self._host = host
        self._usr = usr
        self._passwd = passwd
        self._ssh = None
        self._sftp = None
        self._sftp_connect()
        self._ssh_connect()

    def __del__(self):
        if self._ssh:
            self._ssh.close()
        if self._sftp:
            self._sftp.close()

    def _sftp_connect(self):
        try:
            transport = paramiko.Transport((self._host, 22))
            transport.connect(username=self._usr, password=self._passwd)
            self._sftp = paramiko.SFTPClient.from_transport(transport)
        except Exception as e:
            raise RuntimeError("sftp connect failed [%s]" % str(e))

    def _ssh_connect(self):
        try:
            # 创建ssh对象
            self._ssh = paramiko.SSHClient()
            # 允许连接不在know_hosts文件中的主机
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 连接服务器
            self._ssh.connect(hostname=self._host,
                              port=22,
                              username=self._usr,
                              password=self._passwd,
                              timeout=5)
        except Exception:
            raise RuntimeError("ssh connected to [host:%s, usr:%s, passwd:%s] failed" %
                               (self._host, self._usr, self._passwd))

    def ssh_exec_cmd(self, cmd, path='~'):
        """
        通过ssh连接到远程服务器，执行给定的命令
        :param cmd: 执行的命令
        :param path: 命令执行的目录
        :return: 返回结果
        """
        try:
            result = self._exec_command('cd ' + path + ';' + cmd)
            #print(result)
            return result
        except Exception:
            raise RuntimeError('exec cmd [%s] failed' % cmd)

    def ssh_exec_shell(self, local_file, remote_file):
        """
        执行远程的sh脚本文件
        :param local_file: 本地shell文件
        :param remote_file: 远程shell文件
        :param exec_path: 执行目录
        :return:
        """
        try:
            self._check_remote_file(local_file, remote_file)

            #result = self._exec_command('chmod +x ' + remote_file + '; cd' + exec_path + ';/bin/bash ' + remote_file)
            #print('exec shell result: ', result)
        except Exception as e:
            raise RuntimeError('ssh exec shell failed [%s]' % str(e))


    @staticmethod
    def is_file_exist(file_name):
        try:
            with open(file_name, 'r'):
                return True
        except Exception as e:
            return False

    def _check_remote_file(self, local_file, remote_file):
        """
        检测远程的脚本文件和当前的脚本文件是否一致，如果不一致，则上传本地脚本文件
        :param local_file:
        :param remote_file:
        :return:
        """
        try:

            self._upload_file(local_file, remote_file)
        except Exception as e:
            raise RuntimeError("upload error [%s]" % str(e))


    def _upload_file(self, local_file, remote_file):
        """
        通过sftp上传本地文件到远程
        :param local_file:
        :param remote_file:
        :return:
        """
        try:
            self._sftp.put(local_file, remote_file)
        except Exception as e:
            raise RuntimeError('upload failed [%s]' % str(e))

    def _exec_command(self, cmd):
        """
        通过ssh执行远程命令
        :param cmd:
        :return:
        """
        try:
            stdin, stdout, stderr = self._ssh.exec_command(cmd)
            return stdout.read().decode()
        except Exception as e:
            raise RuntimeError('Exec command [%s] failed' % str(cmd))


class kube_control():
    def __init__(self):
        self.node = "node2"
        self.namespace = "sock-shop"
    def get_all_app(self):#获取特定namespaces 下sock-shop的所有应用
        node_pod_infos = []
        cmd  = "kubectl get pods -n  "+self.namespace+" -o wide |grep "+self.node
        print (cmd)
        ssh = SSHManager("10.121.221.8", "root", "public")
        result = ssh.ssh_exec_cmd(cmd)
        pods = result.split("\n")
        print (pods)
        for item in pods[:-1]:
            pod_infos = item.split()
            node_pod_infos.append(pod_infos)
        return node_pod_infos
        """
        #打印应用总数
        print (self.node_pod)
        for i in self.node_pod:
            print (len(self.node_pod[i]))
        """
    def get_app_docker(self,pods_name):#获取pods 对应的docker 容器ID
        pod_name_docker_dict = {}#以pod 名字为key ，docker 容器id为value
        for pod_name in pods_name:
            cmd = """docker ps --filter name=%s --format '{{.ID}}: {{.Names}}'"""%(pod_name)
            #print (cmd)
            ssh = SSHManager("10.121.221.9", "root", "public")
            result = ssh.ssh_exec_cmd(cmd)
            result_list = result.split("\n")
            for item in result_list:
                if "POD" in item or not item:
                    continue
                pod_name_docker_dict[pod_name] = item.split(":")[0]
        return pod_name_docker_dict

    def set_network_space(self,docker_id):#设置容器的网络空间
        ssh = SSHManager("10.121.221.9", "root", "public")
        cmd_docker_pid = "docker inspect %s|grep Pid"%(docker_id)#获取容器进程号
        print (cmd_docker_pid)
        docker_pid = ssh.ssh_exec_cmd(cmd_docker_pid).split("\n")[0].split(":")[1].strip().replace(",","")
        print (docker_pid)
        cmd_docker_ln = "ln -s /proc/%s/ns/net /var/run/netns/%s" % (docker_pid, docker_id)  # 将进程网络命名空间恢复到主机目录
        ssh.ssh_exec_cmd(cmd_docker_ln)
    def run(self):
        node_pods_infos = self.get_all_app()
        pods_name = []  #改node 所有的pod
        for pod_info in node_pods_infos:
            pods_name.append(pod_info[0])
        pods_name_ids = self.get_app_docker(pods_name)
        print (pods_name_ids)
        print (len(pods_name_ids))
        for pod_name in pods_name_ids:
            print (pod_name)
            self.set_network_space(pods_name_ids[pod_name])#将docker id传入
        return  pods_name_ids
#舍弃ssh连接每个node 防止一个export，值扫描本机的容器
#ip

#site-package安装目录下的egg文件：/usr/lib64/python2.6/site-packages/cython_build_test-0.0.0-py2.6.egg-info
if __name__ == "__main__":
    app = kube_control()
    pods_name_ids  =  app.run()
    print ("dsdsdssds")
    print (pods_name_ids)
    #app.set_network_space("21d59e77a52d")
    #pods = app.get_all_app()
    #print (pods)
    #app.get_app_docker("carts-55f7f5c679-xkd2q")
