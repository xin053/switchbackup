## 交换机配置自动备份

使用 `python3` 多线程 `ssh` 批量登录交换机并获取到交换机配置，自动删除 `30` 天以前的配置，将命令配置到 `crontab` 实现每天备份，支持新华三，华为，锐捷，思科交换机

### 安装依赖

```shell
# python3 环境
# ubuntu
apt install -y python3-pip
# centos
yum install -y python3-pip

# pip3 更新并设置源
pip3 install pip --upgrade -i https://mirrors.aliyun.com/pypi/simple/
pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/

cd /opt
git clone https://github.com/xin053/switchbackup
cd switchbackup
pip3 install -r requirements.txt
```

### 修改配置文件 `hosts.yaml`

按照以下格式, 注意缩进, `yaml` 文件对缩进要求很严格

支持的 `type` 有 `h3c, huawei, ruijie, cisco`

```yaml
# 备份文件保存路径
backup_path: '/home/xin053/swConfigBackup'
# 备份文件保存时长, 单位: 天
keep_time: 30
hosts:
    - name: xxxH3C6800
      type: h3c
      ip: xxx.xxx.xxx.xxx
      port: 22
      username: xxx
      password: xxx
    - name: xxxCE6810-01
      type: huawei
      ip: xxx.xxx.xxx.xxx
      port: 22
      username: xxx
      password: xxx
```

### 使用

```shell
# 命令格式
python3 switchbackup.py [ip] [ip] ...

cd /opt/switchbackup
# 备份配置文件中的全部交换机
python3 switchbackup.py
# 备份配置文件中指定交换机
python3 switchbackup.py xxx.xxx.xxx.xxx xxx.xxx.xxx.xxx
```

### 配置 `crontab`

每天凌晨执行备份:

```shell
0 0 * * * cd /opt/switchbackup && python3 switchbackup.py
```

### 效果图

![](./images/switch.png)
