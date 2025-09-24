import logging
import requests
import datetime
from tokendb import token_db

# 配置基本日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 常量
TOKEN_PASSWORD_URL = "https://as.hypergryph.com/user/auth/v1/token_by_phone_password"
HEADER_LOGIN = {
    'User-Agent': 'Skland/1.0.1 (com.hypergryph.skland; build:100001014; Android 31; ) Okhttp/4.11.0',
    'Accept-Encoding': 'gzip',
    'Connection': 'close'
}


def login_by_password(phone, password):
    """
    通过手机号和密码登录，获取token
    """
    response = requests.post(TOKEN_PASSWORD_URL, json={"phone": phone, "password": password},
                             headers=HEADER_LOGIN).json()
    if response.get('status') != 0:
        raise Exception(f'登录失败：{response["msg"]}')
    token = response['data']['token']
    logging.info(f'登录成功，获取的 token 为：{token}')
    return token


def update_token_for_user(phone, password):
    """
    更新单个用户的token
    """
    try:
        token = login_by_password(phone, password)
        token_db.save_token(phone, password, token)
        logging.info(f'帐号 {phone} 的token更新成功')
        return True
    except Exception as e:
        logging.error(f'帐号 {phone} 更新token失败：{str(e)}')
        return False


def batch_update_tokens(existing_users):
    """
    批量更新所有用户的token
    """
    if not existing_users:
        logging.warning('没有找到已保存的账号，无法批量更新。')
        return {}
    
    updated_users = existing_users.copy()
    for key, user_info in existing_users.items():
        # 从"帐号"字段获取实际手机号
        phone = user_info.get('帐号', '')
        password = user_info['密码']
        try:
            token = login_by_password(phone, password)
            updated_users[key]['token'] = token
            updated_users[key]['更新日期'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logging.info(f'帐号 {phone} 的token更新成功')
        except Exception as e:
            logging.error(f'帐号 {phone} 更新token失败：{str(e)}')
    
    if updated_users:
        token_db.batch_update_tokens(updated_users)
    
    return updated_users
