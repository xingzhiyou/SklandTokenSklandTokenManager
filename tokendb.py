import json
import logging
import os
import datetime

# 配置基本日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TokenDatabase:
    """
    Token数据库管理类，负责处理token的存储、加载和更新操作
    """
    
    def __init__(self, file_name='tokens.json'):
        """
        初始化数据库
        """
        self.file_name = file_name
    
    def load_tokens(self):
        """
        从JSON文件中加载已有的用户信息
        """
        if not os.path.exists(self.file_name):
            logging.warning(f'文件 {self.file_name} 不存在，返回空字典')
            return {}
        try:
            with open(self.file_name, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.error(f'文件 {self.file_name} 格式错误')
            return {}
        except Exception as e:
            logging.error(f'加载文件 {self.file_name} 时发生错误：{str(e)}')
            return {}
    
    def save_token(self, phone, password, token):
        """
        将帐号、密码和token保存到JSON文件中，并记录日期
        """
        try:
            data = self.load_tokens()
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 标准化输入的手机号格式（移除非数字字符）
            normalized_phone = ''.join(filter(str.isdigit, phone))
            
            # 查找是否存在相同的手机号（通过比较"帐号"字段）
            existing_key = None
            for key, user_info in data.items():
                # 获取存储在"帐号"字段中的手机号并标准化
                stored_phone = user_info.get("帐号", "")
                normalized_stored = ''.join(filter(str.isdigit, stored_phone))
                if normalized_stored == normalized_phone:
                    existing_key = key
                    break
            
            # 如果存在相同的手机号，则使用现有的键更新数据
            # 否则，为新用户创建一个新键
            if existing_key:
                # 更新现有用户的数据
                data[existing_key].update({
                    "密码": password,
                    "token": token,
                    "更新日期": current_time
                })
            else:
                # 为新用户创建一个新的键和条目
                # 使用手机号作为键名
                data[phone] = {
                    "帐号": phone,
                    "密码": password,
                    "token": token,
                    "更新日期": current_time
                }
            
            with open(self.file_name, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logging.info(f'数据已保存到 {self.file_name}')
            logging.info(f'更新日期: {current_time}')
            return True
        except Exception as e:
            logging.error(f'保存数据时发生错误：{str(e)}')
            return False
    
    def batch_update_tokens(self, updated_users):
        """
        批量更新用户token信息
        """
        try:
            with open(self.file_name, 'w', encoding='utf-8') as f:
                json.dump(updated_users, f, ensure_ascii=False, indent=4)
            logging.info('批量更新完成')
            return True
        except Exception as e:
            logging.error(f'批量更新时发生错误：{str(e)}')
            return False
    
    def get_user_count(self):
        """
        获取用户数量
        """
        tokens = self.load_tokens()
        return len(tokens)


# 创建全局实例以便外部直接使用
token_db = TokenDatabase()
