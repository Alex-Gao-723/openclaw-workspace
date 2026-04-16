#!/usr/bin/env python3
"""
每日邮件检查脚本 - 连接QQ邮箱获取未读邮件
"""

import imaplib
import email
import json
from email.header import decode_header
from datetime import datetime

def decode_str(s):
    """解码邮件标题/发件人"""
    if not s:
        return ""
    value, charset = decode_header(s)[0]
    if isinstance(value, bytes):
        return value.decode(charset or 'utf-8', errors='ignore')
    return value

def get_email_body(msg):
    """获取邮件正文（用于后续扩展）"""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')[:200]
                except:
                    pass
            elif content_type == "text/html":
                try:
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')[:200]
                except:
                    pass
    else:
        try:
            return msg.get_payload(decode=True).decode('utf-8', errors='ignore')[:200]
        except:
            pass
    return ""

def check_emails():
    """检查未读邮件"""
    # QQ邮箱配置
    EMAIL = "280956117@qq.com"
    PASSWORD = "klzwqfhhklaabifi"  # 授权码
    IMAP_SERVER = "imap.qq.com"
    
    try:
        # 连接IMAP服务器
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993)
        mail.login(EMAIL, PASSWORD)
        mail.select('inbox')
        
        # 搜索未读邮件
        status, messages = mail.search(None, 'UNSEEN')
        
        unread_emails = []
        
        if status == 'OK' and messages[0]:
            msg_ids = messages[0].split()
            
            # 获取最近的20封未读邮件
            for msg_id in msg_ids[-20:]:
                status, msg_data = mail.fetch(msg_id, '(RFC822)')
                
                if status == 'OK':
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # 解析邮件信息
                    subject = decode_str(msg.get("Subject", "无主题"))
                    from_header = msg.get("From", "未知发件人")
                    date_header = msg.get("Date", "")
                    
                    # 解析发件人
                    from_parts = email.utils.parseaddr(from_header)
                    sender_name = decode_str(from_parts[0]) if from_parts[0] else from_parts[1]
                    sender_email = from_parts[1]
                    sender = f"{sender_name} <{sender_email}>" if sender_name != sender_email else sender_email
                    
                    unread_emails.append({
                        "subject": subject,
                        "sender": sender,
                        "sender_email": sender_email,
                        "date": date_header
                    })
        
        mail.logout()
        
        return {
            "success": True,
            "unread_count": len(unread_emails),
            "emails": unread_emails,
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "unread_count": 0,
            "emails": [],
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

if __name__ == "__main__":
    result = check_emails()
    print(json.dumps(result, ensure_ascii=False, indent=2))
