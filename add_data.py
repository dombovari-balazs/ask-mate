import connection
import utility
from psycopg2 import sql
import security



@connection.connection_handler
def question(cursor, title, message, user_id):
    data = {
        'submission_time': utility.get_date_time(),
        'view_number': 0,
        'vote_number': 0,
        'title': title,
        'message': message,
        'image': None,
        'user_id': user_id,
        'voted_users': []
    }
    cursor.execute(
        sql.SQL("""
                INSERT INTO question (submission_time, view_number, vote_number, title, message, image, user_id, voted_users)
                VALUES (%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s,
                %(user_id)s, %(voted_users)s);
                
                SELECT MAX(id) FROM question;
        """), data
    )
    question_id = cursor.fetchone()
    return question_id['max']


@connection.connection_handler
def answer(cursor, message, question_id, user_id):
    data = {
        'submission_time': utility.get_date_time(),
        'vote_number': 0,
        'question_id': question_id,
        'message': message,
        'image': None,
        'user_id': user_id
    }
    cursor.execute(
        sql.SQL("""
               INSERT INTO answer (submission_time, vote_number, question_id, message, image, user_id)
               VALUES (%(submission_time)s, %(vote_number)s, %(question_id)s, %(message)s, %(image)s, %(user_id)s); 
        """), data
    )


@connection.connection_handler
def comment(cursor, message, question_id, user_id, answer_id=None):
    data = {
        'question_id': question_id,
        'answer_id': answer_id,
        'message': message,
        'submission_time': utility.get_date_time(),
        'edited_count': 0,
        'user_id': user_id
    }
    cursor.execute(
        sql.SQL("""
                INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count, user_id)
                VALUES (%(question_id)s, %(answer_id)s, %(message)s, %(submission_time)s, %(edited_count)s, %(user_id)s) 
        """), data
    )


@connection.connection_handler
def registration(cursor, data):
    data.update({'registration_time': utility.get_date_time(),
                 'reputation': 0,
                 'hashed_pw': security.hash_password(data['password'])})
    cursor.execute(
        sql.SQL('''
                INSERT INTO users (user_name, hashed_pw, reputation, registration_time)
                VALUES (%(username)s, %(hashed_pw)s, %(reputation)s, %(registration_time)s);
        '''), data
    )
