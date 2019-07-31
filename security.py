import bcrypt
import connection


def hash_password(plain_text_password):
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(plain_text_password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)


@connection.connection_handler
def login(cursor, user_name, text_password):    #todo validate wrong username search, int password nem jo
    cursor.execute('''
                    SELECT hashed_pw FROM users
                    WHERE user_name = %s;
    ''', (user_name,))
    hashed_pw = cursor.fetchone()
    if hashed_pw is None:
        return False
    return verify_password(text_password, hashed_pw['hashed_pw'])
