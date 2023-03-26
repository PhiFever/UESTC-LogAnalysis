from datetime import datetime
import requests
import yaml
from flask import Flask
from IPy import IP
from exts import db
from modules import event
from logParse import get_message_list
from cronConfig import read_config

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)


def get_ip():
    # return requests.get('http://myip.ipip.net', timeout=5).text
    url = 'https://ip.cn/api/index?ip=&type=0'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    return response.json()['ip']


def insert_data(data):
    event_data_list = data[0]
    d_ip = get_ip()  # "192.168.44.136"

    # print(d_ip)
    # for e_data in event_data_list:
    #     print(e_data)

    for e_data in event_data_list:
        e = event(e_data["log_type"], e_data["username"], IP(e_data["s_ip"]).int(), e_data["s_port"], IP(d_ip).int(),
                  e_data["d_port"], e_data["time"])
        print(e_data)
        print(e)
        # ip需要特殊转换
        db.session.add(e)
    db.session.commit()


if __name__ == "__main__":
    path = r'config/updateDBConfig.yaml'
    config = read_config(path)
    log_path = config["log_path"]
    last_update_time = datetime.strptime(config["last_update_time"], "%Y-%m-%d %H:%M:%S")
    last_d_port = config["last_d_port"]

    # 写入数据库
    data = get_message_list(log_path, last_d_port, last_update_time)
    with app.app_context():
        insert_data(data)
    print(f"insert data successfully,{datetime.now()}")

    # 更新配置文件
    cur_d_port = data[1]
    cur_time = data[2].strftime("%Y-%m-%d %H:%M:%S")
    yaml_update = {"log_path": log_path, "last_update_time": cur_time, "last_d_port": cur_d_port}
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_update, f, allow_unicode=False)