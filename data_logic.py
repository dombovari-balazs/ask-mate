from psycopg2 import sql
import connection
import datetime


question_fieldnames = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
answer_fieldnames = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


@connection.connection_handler
def get_all_rows(cursor, table_name, order_key, order_type='desc', limit_count='NULL', off_count='0'):
    cursor.execute(
        sql.SQL('''
                    SELECT * FROM {table}
                    ORDER BY {order_key} {order_type} LIMIT {limit_count} OFFSET {off_count};
    ''').format(table=sql.Identifier(table_name), order_key=sql.Identifier(order_key), order_type=sql.SQL(order_type),
                limit_count=sql.SQL(limit_count), off_count=sql.Literal(off_count)))
    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def get_single_row(cursor, row, table_name, column_name='id'):
    cursor.execute(
        sql.SQL("""
                SELECT * FROM {table}
                WHERE {column_name} = %(row)s;
    """).format(table=sql.Identifier(table_name), column_name=sql.Identifier(column_name)), {'row': row})
    single_row = cursor.fetchone()
    return single_row


@connection.connection_handler
def add_view(cursor, question_id):
    cursor.execute('''
                    UPDATE question
                    SET view_number = view_number + 1
                    WHERE id = %(id)s;
                    ''', {'id': question_id})


@connection.connection_handler
def vote_counter(cursor, question_id, direction):
    if direction =='up':
        cursor.execute("""
                        UPDATE question
                        SET vote_number = vote_number + 1, view_number = view_number - 1 
                        WHERE id = %(question_id)s;
                        """, {'question_id': question_id})
    else:
        cursor.execute("""
                       UPDATE question
                       SET vote_number = vote_number - 1, view_number = view_number - 1 
                       WHERE id = %(question_id)s;
                        """, {'question_id': question_id})


@connection.connection_handler
def edit_question(cursor, question_id, newdata):
    cursor.execute("""
                    UPDATE question
                    SET message = %(message)s
                    WHERE id = %(id)s;
                    """,{'message': newdata, 'id': question_id})


@connection.connection_handler
def edit_answer(cursor, answer_id, newdata):
    cursor.execute("""
                    UPDATE answer
                    SET message = %(message)s
                    WHERE id = %(answer_id)s;
                    """, {'message': newdata, 'answer_id': answer_id})


@connection.connection_handler
def delete_question_answers(cursor, question_id):
    cursor.execute("""
                    DELETE FROM answer
                    WHERE question_id = %(question_id)s;
                    """, {'question_id': question_id})


@connection.connection_handler
def delete_data(cursor, id, table_name):
    cursor.execute(sql.SQL('''
                    DELETE FROM {table}
                    WHERE  id = %(id)s;
                    ''').format(table=sql.Identifier(table_name)), {'id': id})


@connection.connection_handler
def delete_all_comments(cursor, answer_id=None, question_id=None):
    if answer_id is not None:
        cursor.execute('''
                        DELETE FROM comment
                        WHERE answer_id = %(answer_id)s;
                        ''', {'answer_id': answer_id})
    else:
        cursor.execute('''
                        DELETE FROM comment
                        WHERE question_id = %(question_id)s;
                        ''', {'question_id': question_id})


@connection.connection_handler
def get_question_id(cursor, answer_id=None, comment_id=None):
    if answer_id is not None:
        cursor.execute('''
                        SELECT question_id FROM answer
                        WHERE id = %(answer_id)s;
                    ''', {'answer_id': answer_id})
    else:
        cursor.execute('''
                                SELECT question_id FROM comment
                                WHERE id = %(comment_id)s;
                    ''', {'comment_id': comment_id})
    raw_id = cursor.fetchone()
    return raw_id['question_id']


@connection.connection_handler
def edit_comment(cursor, comment_id, message):
    cursor.execute('''
                    UPDATE comment
                    SET edited_count = edited_count + 1, message = %(message)s
                    WHERE id = %(comment_id)s;
    ''', {'comment_id': comment_id,
          'message': message}
                   )


@connection.connection_handler
def search_questions(cursor, quote):
    cursor.execute('''
                    SELECT id FROM question
                    WHERE message LIKE %(quote)s OR title LIKE %(quote)s;
    ''', {'quote': '%' + quote + '%'})
    question_ids = cursor.fetchall()
    return question_ids


@connection.connection_handler
def search_answers(cursor, quote):
    cursor.execute('''
                    SELECT question_id FROM answer
                    WHERE message LIKE %(quote)s;
    ''', {'quote': '%' + quote + '%'})
    answer_ids = cursor.fetchall()
    for line in answer_ids:
        line['id'] = line.pop('question_id')
    return answer_ids


def convert_search_result(ids):
    processed_ids = []
    for line in ids:
        processed_ids.append(line['id'])
    return set(processed_ids)


@connection.connection_handler
def question_search_result(cursor, ids):
    ids = tuple(ids)
    cursor.execute('''
                    SELECT * FROM question
                    WHERE id IN %(id_list)s; 
    ''', {'id_list': tuple(ids)})
    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def get_latest_questions(cursor):
    cursor.execute("""
                    SELECT * FROM question
                    ORDER BY id desc LIMIT 5;
    """)
    questions = cursor.fetchall()
    return questions


