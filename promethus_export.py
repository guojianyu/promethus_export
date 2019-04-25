# -*- coding: utf-8 -*-
# @Time    : 2019/4/15 10:36
# @Author  : 郭建宇
# @Email   : 276381225@qq.com
# @File    : 1.py
# @Software: PyCharm
import os
import time
import subprocess
import random
from prometheus_client import Gauge,start_http_server,Counter
from prometheus_client import Gauge
import get_netspaces

def pod_name_cmd (k8s_node_name):
    """
    :param pods_name_ids:字典pod的名字是key ,dokcer 容器id是value
    :return:
    """
    #应用与端口的对应关系
    app_port = {
        "carts-db":"27017",
        "carts":"80",
        "catalogue-db":"3306" ,
        "catalogue": "80",
        "front-end":  "8079",
        "orders-db": "27017",
        "orders": "80",
        "payment": "80",
        "queue-master": "80",
        "rabbitmq": "5672",
        "shipping": "80",
        "user-db": "27017",
        "user": "80",
    }

    app = get_netspaces.kube_control()
    pods_name_ids = app.run()
    print (pods_name_ids)
    if not pods_name_ids:
        return
    pod_name_app_name = {}#key wei pod 名字，value是app名字
    for pod_name,docker_id in pods_name_ids.items():
        for app_name in  app_port:
            if app_name in pod_name:
                if "-db" not in app_name and "-db" not in pod_name:
                    pod_name_app_name[pod_name] = app_name
                    break
                if "-db" in app_name and "-db"  in pod_name:
                    pod_name_app_name[pod_name] = app_name
                    break
    print (pod_name_app_name)#找到pod 与app对应关系
    pod_name_cmd = {}
    for pod_name,app_name in pod_name_app_name.items():
        docker_id = pods_name_ids[pod_name]
        port = app_port[app_name]
        cmd = "ip netns exec %s ss -it sport = :%s"%(docker_id,port)
        pod_name_cmd[pod_name] = cmd
    return pod_name_cmd




def server_run(k8s_node,mylabels=['ESTAB','retrans','retrans0','retrans1','lastsnd', 'rcvmss', 'advmss', 'cubicwscale', 'cubicwscale0','cubicwscale1','rto', 'segs_in', 'mss', 'send', 'segs_out', 'rtt', 'rtt0','rtt1','lastack', 'lastrcv', 'pacing_rate', 'ato', 'rcv_space', 'rcv_rtt', 'bytes_received', 'cwnd', 'bytes_acked']):
    pro_pro = "sock_shop_" #promths 前缀
    g = Gauge(pro_pro+k8s_node+"_carts_db", 'Description of gauge',mylabels)
    g1 = Gauge(pro_pro+k8s_node+"_carts", 'Description of gauge',mylabels)
    g2 = Gauge(pro_pro + k8s_node + "_catalogue_db", 'Description of gauge', mylabels)
    g3 = Gauge(pro_pro + k8s_node + "_catalogue", 'Description of gauge', mylabels)
    g4 = Gauge(pro_pro + k8s_node + "_front_end", 'Description of gauge', mylabels)
    g5 = Gauge(pro_pro + k8s_node + "_orders_db", 'Description of gauge', mylabels)
    g6 = Gauge(pro_pro + k8s_node + "_orders", 'Description of gauge', mylabels)
    g7 = Gauge(pro_pro + k8s_node + "_payment", 'Description of gauge', mylabels)
    g8 = Gauge(pro_pro + k8s_node + "_queue_master", 'Description of gauge', mylabels)
    g9 = Gauge(pro_pro + k8s_node + "_rabbitmq", 'Description of gauge', mylabels)
    g10 = Gauge(pro_pro + k8s_node + "_shipping", 'Description of gauge', mylabels)
    g11 = Gauge(pro_pro + k8s_node + "_user_db", 'Description of gauge', mylabels)
    g12 = Gauge(pro_pro + k8s_node + "_user", 'Description of gauge', mylabels)
    # 此时一定要注意,定义Gague标签的时候是一个列表,列表可以存多个lablename,类型是字符串
    # 在给lable定义value的时候也要注意,mylablename 这里是一个方法,或者说是一个变量了,一定要注意.
    start_http_server(8000)
    while True:
        time.sleep(5)
        tmp_dict = {'retrans': '', 'rto': '', 'lastrcv': '', 'rtt': '', 'ESTAB': '',
                    'rtt0': '', 'rtt1': '', 'retrans0': '', 'retrans1': '',
                    'bytes_received': '', 'rcv_space': '',
                    'lastsnd': '', 'mss': '', 'send': '903.5Kbps',
                    'segs_out': '', 'advmss': '', 'rcv_rtt': '',
                    'ssthresh': '', 'unacked': '', 'lastack': '',
                    'cubicwscale': '8,7', 'cubicwscale0': '', 'cubicwscale1': '', 'pacing_rate': '1.8Mbps',
                    'segs_in': '', 'bytes_acked': '',
                    'rcvmss': '', 'ato': '', 'cwnd': ''
                    }
        pod_name_c = pod_name_cmd(k8s_node)
        if not pod_name_c:
            continue
        for pod_name,cmd in pod_name_c.items():
            tmp_dict_tmp = run_cmd(cmd)
            if  tmp_dict_tmp:
                for item in tmp_dict_tmp:
                    tmp_dict[item] = tmp_dict_tmp[item]
                if "/" in tmp_dict["retrans"]:
                    tmp_dict['retrans0'],tmp_dict['retrans1'] = tmp_dict["retrans"].split("/")
                else:
                    tmp_dict['retrans0'], tmp_dict['retrans1'] = "",""
                if "/" in tmp_dict["rtt"]:
                    tmp_dict['rtt0'],tmp_dict['rtt1'] = tmp_dict["rtt"].split("/")
                else:
                    tmp_dict['rtt0'], tmp_dict['rtt1'] = "",""
                if "," in tmp_dict["cubicwscale"]:
                    tmp_dict['cubicwscale0'],tmp_dict['cubicwscale1'] = tmp_dict["cubicwscale"].split(",")
                else:
                    tmp_dict['cubicwscale0'], tmp_dict['cubicwscale1'] = "",""
                if 'bps' in tmp_dict["send"]:
                    try:
                        if 'K' in tmp_dict["send"]:
                            tmp_dict["send"] = str (float(tmp_dict["send"].replace("Kbps",""))*1024) +"bps"
                        if 'M' in tmp_dict["send"]:
                            tmp_dict["send"] = str(float(tmp_dict["send"].replace("Mbps", "")) * 1024*1024) + "bps"
                        if 'G' in tmp_dict["send"]:
                            tmp_dict["send"] = str(float(tmp_dict["send"].replace("Gbps", "")) * 1024 * 1024 *1024) + "bps"
                    except Exception as e:
                        print (e)
                if 'bps' in tmp_dict['pacing_rate']:
                    try:
                        if 'K' in tmp_dict["pacing_rate"]:
                            tmp_dict["pacing_rate"] = str(float(tmp_dict["pacing_rate"].replace("Kbps", "")) * 1024) + "bps"
                        if 'M' in tmp_dict["pacing_rate"]:
                            tmp_dict["pacing_rate"] = str(float(tmp_dict["pacing_rate"].replace("Mbps", "")) * 1024 * 1024) + "bps"
                        if 'G' in tmp_dict["pacing_rate"]:
                            tmp_dict["pacing_rate"] = str(float(tmp_dict["pacing_rate"].replace("Gbps", "")) * 1024 * 1024 * 1024) + "bps"
                    except Exception as e:
                        print(e)
            if "carts-db" in pod_name:
                s = g
            elif "carts" in pod_name:
                s = g1
            elif "catalogue-db" in pod_name:
                s = g2
            elif "catalogue" in pod_name:
                s = g3
            elif "front-end" in pod_name:
                s = g4
            elif "orders-db" in pod_name:
                s = g5
            elif "orders" in pod_name:
                s = g6
            elif "payment" in pod_name:
                s = g7
            elif "queue-master" in pod_name:
                s = g8
            elif "rabbitmq" in pod_name:
                s = g9
            elif "shipping" in pod_name:
                s = g10
            elif "user-db" in pod_name:
                s = g11
            elif "user" in pod_name:
                s = g12

            s.labels(ESTAB =tmp_dict["ESTAB"],
                     lastsnd=tmp_dict["lastsnd"],rcvmss=tmp_dict["rcvmss"],advmss=tmp_dict["advmss"],
                     cubicwscale =tmp_dict["cubicwscale"],rto=tmp_dict["rto"],segs_in=tmp_dict["segs_in"],
                     mss=tmp_dict["mss"],send=tmp_dict["send"],segs_out=tmp_dict["segs_out"],
                     rtt=tmp_dict["rtt"],lastack=tmp_dict["lastack"],lastrcv=tmp_dict["lastrcv"],
                     retrans=tmp_dict["retrans"],
                     cubicwscale0 = tmp_dict['cubicwscale0'],cubicwscale1 = tmp_dict['cubicwscale1'],
                     rtt0=tmp_dict['rtt0'],rtt1=tmp_dict['rtt1'],retrans0=tmp_dict['retrans0'],retrans1=tmp_dict['retrans1'],
                     pacing_rate = tmp_dict["pacing_rate"],ato=tmp_dict["ato"],rcv_space=tmp_dict["rcv_space"],
                     rcv_rtt = tmp_dict["rcv_rtt"],bytes_received=tmp_dict["bytes_received"],cwnd=tmp_dict["cwnd"],
                    bytes_acked = tmp_dict["bytes_acked"]
                     ).set(time.time())


def run_cmd(cmd):
    tmp_dict = {}
    try:
        #res = os.popen("ss -it dport = :"+str(port)).read()
        #res = os.popen("ip netns exec 5c0cbd5c588a ss -it sport = :27017").read()
        res = os.popen("ip netns exec 5c0cbd5c588a ss -it sport = :27017").read()
        cmd_res = res.split("\n")[1:-1]
        tmp_dict["ESTAB"] = cmd_res[-2]
        tmp = cmd_res[-1].strip().split()
        tmp[0] = tmp[0] + "" + tmp[1]
        tmp.pop(1)
        print (tmp)
        if not tmp:
            return
        for num,item in enumerate(tmp,0):
            if ":" not in item and ":" not in tmp[num+1]:
                tmp[num] = tmp[num] + ":" + tmp[num+1]
        for tmp_s in tmp:
            if ":" not in tmp_s:
                continue
            key,value = tmp_s.split(":")
            tmp_dict[key] = value
        return tmp_dict

    except Exception as e:
        print (e)
        return


if __name__ == "__main__":
    k8s_node_name = "node2"
    server_run(k8s_node_name)
    #print (run_cmd())
    #pod_name_cmd(k8s_node_name)