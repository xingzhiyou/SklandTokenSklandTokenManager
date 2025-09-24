import logging
from getpass import getpass
from tokendb import token_db
from login_manager import update_token_for_user, batch_update_tokens

# 配置基本日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def print_tokens(tokens):
    """
    输出所有 token，并以逗号分隔
    """
    token_list = []
    for user_info in tokens.values():
        if 'token' in user_info:
            token_list.append(user_info['token'])
    if token_list:
        logging.info(f'所有 token 列表（逗号分隔）：\n{",".join(token_list)}')
    else:
        logging.warning('未找到任何 token')


def print_detailed_info(tokens):
    """
    输出所有用户的详细信息，包括手机号和更新日期
    """
    if not tokens:
        logging.warning('没有用户信息可供显示')
        return
        
    logging.info('\n用户详细信息：')
    logging.info('-' * 70)
    logging.info(f'{"序号":<5} {"手机号":<15} {"更新日期":<20} {"token前10位":<15}')
    logging.info('-' * 70)
    
    index = 1
    for user_info in tokens.values():
        phone = user_info.get('帐号', '')
        update_date = user_info.get('更新日期', '未记录')
        token = user_info.get('token', '')
        token_prefix = token[:10] if token else '无'
        
        logging.info(f'{index:<5} {phone:<15} {update_date:<20} {token_prefix:<15}')
        index += 1
        
    logging.info('-' * 70)


def show_menu():
    """
    显示主菜单
    """
    print('\n===== Token 管理系统 =====')
    print('1. 查看所有 token')
    print('2. 更新单个用户的 token')
    print('3. 批量更新所有用户的 token')
    print('4. 退出')
    print('========================')


def view_all_tokens():
    """
    查看所有用户的 token 信息
    """
    # 加载用户信息
    tokens = token_db.load_tokens()
    if tokens:
        logging.info(f'加载到 {len(tokens)} 个用户的信息')
        print_tokens(tokens)
        print_detailed_info(tokens)
    else:
        logging.warning('未加载到任何用户信息')


def update_single_token():
    """
    更新单个用户的 token，优先使用已保存密码
    """
    existing_users = token_db.load_tokens()
    phone = input('请输入手机号码：')
    
    # 标准化输入的手机号格式（移除非数字字符）
    normalized_phone = ''.join(filter(str.isdigit, phone))
    
    # 查找匹配的手机号
    matched_phone = None
    for key, user_info in existing_users.items():
        # 从"帐号"字段获取手机号并标准化
        stored_phone = user_info.get("帐号", "")
        normalized_stored = ''.join(filter(str.isdigit, stored_phone))
        if normalized_stored == normalized_phone:
            matched_phone = key
            break
    
    if matched_phone:
        logging.info(f'找到已保存的帐号 {existing_users[matched_phone]["帐号"]}，优先使用已保存密码更新 token')
        password = existing_users[matched_phone]["密码"]
        try:
            # 使用已保存密码更新 token
            update_token_for_user(existing_users[matched_phone]["帐号"], password)
            
            # 成功更新后，询问用户是否要更新密码
            if input('\n是否要更新此帐号的保存密码？(y/n，默认为n)') == 'y':
                new_password = getpass(f'请输入新密码(用于更新帐号 {existing_users[matched_phone]["帐号"]})：')
                confirm_password = getpass('请再次输入新密码以确认：')
                
                if new_password == confirm_password:
                    # 即使不登录，也更新保存的密码
                    try:
                        token_db.save_token(existing_users[matched_phone]["帐号"], new_password, existing_users[matched_phone]["token"])
                        logging.info(f'帐号 {existing_users[matched_phone]["帐号"]} 的密码已更新')
                    except Exception as e:
                        logging.error(f'更新密码时发生错误：{str(e)}')
                else:
                    logging.error('两次输入的密码不一致，密码更新失败')
        except Exception as e:
            logging.error(f'使用已保存密码更新 token 失败：{str(e)}')
            if input('是否使用新密码重新登录？(y/n)') == 'y':
                password = getpass(f'请输入新密码(用于更新帐号 {existing_users[matched_phone]["帐号"]})：')
                try:
                    update_token_for_user(existing_users[matched_phone]["帐号"], password)
                except Exception as e:
                    logging.error(f'登录失败：{str(e)}')
            else:
                logging.info('操作取消')
    else:
        password = getpass('请输入密码(不会显示在屏幕上面)：')
        try:
            # 对于新用户，使用输入的原始格式
            update_token_for_user(phone, password)
        except Exception as e:
            logging.error(f'登录失败：{str(e)}')


def main():
    """
    主函数
    """
    while True:
        show_menu()
        choice = input('请输入您的选择（1-4）：')
        
        if choice == '1':
            view_all_tokens()
        elif choice == '2':
            update_single_token()
        elif choice == '3':
            existing_users = token_db.load_tokens()
            if existing_users:
                logging.info(f'将批量更新 {len(existing_users)} 个用户的 token')
                confirm = input('确定要继续吗？(y/n)')
                if confirm.lower() == 'y':
                    batch_update_tokens(existing_users)
                else:
                    logging.info('批量更新已取消')
            else:
                logging.warning('没有找到已保存的账号，无法批量更新。')
        elif choice == '4':
            logging.info('感谢使用 Token 管理系统，再见！')
            break
        else:
            logging.warning('无效的选择，请重新输入')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error(f'程序运行时发生错误：{str(e)}')