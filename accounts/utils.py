import base64
from django.conf import settings
from cryptography.fernet import Fernet

# ENCRYPT_KEY = Fernet.generate_key()

def generate_pw_hash(txt):
    '''
    для безопасного хранения пароля в дб
    '''
    # convert integer etc to string first
    txt = str(txt)
    cipher_suite = Fernet(settings.ENCRYPT_KEY) # key should be byte
    encrypted_text = cipher_suite.encrypt(txt.encode('utf-8'))
    encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode("ascii")
    return encrypted_text

def decrypt_pw_hash(encrypted):
    '''
    для безопасного восстановления пв из дб
    '''
    encrypted = base64.urlsafe_b64decode(encrypted)
    cipher_suite = Fernet(settings.ENCRYPT_KEY)
    decrypted = cipher_suite.decrypt(encrypted).decode("utf-8")     
    return decrypted