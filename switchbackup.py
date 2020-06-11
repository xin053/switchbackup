import concurrent.futures
import datetime
import logging
from multiprocessing import cpu_count
import os
import pathlib
import pexpect
import sys
import time
from ruamel.yaml import YAML


# h3c 交换机配置备份
def H3CAutoConfig(host):
    ssh = pexpect.spawn('ssh -o StrictHostKeyChecking=no -p %s %s@%s ' %
                        (host['port'], host['username'], host['ip']))

    try:
        ssh.expect('[Pp]assword:', timeout=30)
        ssh.sendline(host['password'])
        ssh_info = ssh.expect(['>$', '[Pp]assword:'])
        if ssh_info == 0:
            ssh.sendline('screen-length disable')
            ssh.expect(['>$', ']$'])
            ssh.sendline('dis cur')
            ssh.expect(['>$', ']$'])
            with open(log_filename + '/' + host['ip'] + '.txt', 'w') as f:
                print(ssh.before.decode('utf8', 'ignore').replace('\r', ''),
                      file=f)
            ssh.close()
            logger.info('backup switch {}[{}:{}] successful \n'.format(
                host['name'], host['ip'], host['port']))
        else:
            ssh.close()
            logger.error('switch {}[{}:{}] password error \n'.format(
                host['name'], host['ip'], host['port']))
    except pexpect.EOF:
        ssh.close()
        logger.error('switch {}[{}:{}] ssh failed.(EOF) \n'.format(
            host['name'], host['ip'], host['port']))
    except pexpect.TIMEOUT:
        ssh.close()
        logger.error('switch {}[{}:{}] ssh failed.(TIMEOUT) \n'.format(
            host['name'], host['ip'], host['port']))


# 华为 交换机配置备份
def HuaweiAutoConfig(host):
    ssh = pexpect.spawn('ssh -o StrictHostKeyChecking=no -p %s %s@%s ' %
                        (host['port'], host['username'], host['ip']))

    try:
        ssh.expect('[Pp]assword:', timeout=30)
        ssh.sendline(host['password'])
        ssh_info = ssh.expect(['>$', '[Pp]assword:'])
        if ssh_info == 0:
            ssh.sendline('screen-length 0 temporary')
            ssh.expect(['>$', ']$'])
            ssh.sendline('dis cur')
            ssh.expect(['>$', ']$'])
            with open(log_filename + '/' + host['ip'] + '.txt', 'w') as f:
                print(ssh.before.decode('utf8', 'ignore').replace('\r', ''),
                      file=f)
            ssh.close()
            logger.info('backup switch {}[{}:{}] successful \n'.format(
                host['name'], host['ip'], host['port']))
        else:
            ssh.close()
            logger.error('switch {}[{}:{}] password error \n'.format(
                host['name'], host['ip'], host['port']))
    except pexpect.EOF:
        ssh.close()
        logger.error('switch {}[{}:{}] ssh failed.(EOF) \n'.format(
            host['name'], host['ip'], host['port']))
    except pexpect.TIMEOUT:
        ssh.close()
        logger.error('switch {}[{}:{}] ssh failed.(TIMEOUT) \n'.format(
            host['name'], host['ip'], host['port']))


# 锐捷/思科 交换机配置备份
def RuijieAutoConfig(host):
    ssh = pexpect.spawn('ssh -o StrictHostKeyChecking=no -p %s %s@%s ' %
                        (host['port'], host['username'], host['ip']))

    try:
        ssh.expect('[Pp]assword: ', timeout=30)
        ssh.sendline(host['password'])
        ssh_info = ssh.expect(['#$', '[Pp]assword:'])
        if ssh_info == 0:
            ssh.sendline('terminal length 0')
            ssh.expect('#$')
            ssh.sendline('sh run')
            ssh.expect('#$')
            with open(log_filename + '/' + host['ip'] + '.txt', 'w') as f:
                print(ssh.before.decode('utf8', 'ignore').replace('\r', ''),
                      file=f)
            ssh.close()
            logger.info('backup switch {}[{}:{}] successful \n'.format(
                host['name'], host['ip'], host['port']))
        else:
            ssh.close()
            logger.error('switch {}[{}:{}] password error \n'.format(
                host['name'], host['ip'], host['port']))
    except pexpect.EOF:
        ssh.close()
        logger.error('switch {}[{}:{}] ssh failed.(EOF) \n'.format(
            host['name'], host['ip'], host['port']))
    except pexpect.TIMEOUT:
        ssh.close()
        logger.error('switch {}[{}:{}] ssh failed.(TIMEOUT) \n'.format(
            host['name'], host['ip'], host['port']))


# 检测主机端口是否连通
def host_alive(host):
    i = os.system('nc -zv {} {} -w 5'.format(host['ip'], host['port']))
    if i != 0:
        logger.error('switch {}[{}:{}] is unreachable \n'.format(
            host['name'], host['ip'], host['port']))
        return False
    return True


def backup(host):
    if host['type'] == 'h3c':
        H3CAutoConfig(host)
    elif host['type'] == 'huawei':
        HuaweiAutoConfig(host)
    elif host['type'] == 'ruijie':
        RuijieAutoConfig(host)
    elif host['type'] == 'cisco':
        RuijieAutoConfig(host)
    else:
        logger.error('switch {}[{}:{}] is not support \n'.format(
            host['name'], host['ip'], host['port']))


# load config file
config_file = pathlib.Path(r'./hosts.yaml')
yaml = YAML(typ='safe')
config = yaml.load(config_file)

date_date = datetime.datetime.now().strftime('%Y-%m-%d')
log_filename = config['backup_path'] + os.sep + date_date
os.system('mkdir -p %s' % log_filename)

# init logger
logger = logging.getLogger()
logger.setLevel('DEBUG')
BASIC_FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
chlr = logging.StreamHandler()  # 输出到控制台的handler
chlr.setFormatter(formatter)
chlr.setLevel('DEBUG')  # 也可以不设置，不设置就默认用logger的level
fhlr = logging.FileHandler(filename=log_filename + '/error-' + str(date_date) +
                           '.log',
                           mode='a+',
                           encoding='utf8')  # 输出到文件的handler
fhlr.setFormatter(formatter)
logger.addHandler(chlr)
logger.addHandler(fhlr)

cpus = cpu_count()

alive_host = []

if len(sys.argv) > 1:
    for host in config['hosts']:
        if host['ip'] in sys.argv[1:] and host_alive(host):
            alive_host.append(host)
else:
    for host in config['hosts']:
        if host_alive(host):
            alive_host.append(host)

with concurrent.futures.ThreadPoolExecutor(max_workers=cpus) as executor:
    submits = [executor.submit(backup, host) for host in alive_host]
    for future in concurrent.futures.as_completed(submits):
        future.result()

nowtime = datetime.datetime.now()
# 删除过期的配置文件
backup_filelist = list(os.listdir(config['backup_path']))
for backup_file in backup_filelist:
    filetime = datetime.datetime.fromtimestamp(
        os.path.getmtime(config['backup_path'] + os.sep + backup_file))
    if (nowtime - filetime).seconds > config['keep_time'] * 24 * 3600:
        logger.info('delete backup files before {} days[{}]'.format(
            config['keep_time'], filetime))
        os.system('rm -rf ' + config['backup_path'] + os.sep + backup_file)
