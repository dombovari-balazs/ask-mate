from psycopg2 import sql
import connection

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
def _get_single_row(cursor, row, table_name, column_name='id'):
    cursor.execute(
        sql.SQL("""
                SELECT * FROM {table}
                WHERE {column_name} = %(row)s;
    """).format(table=sql.Identifier(table_name), column_name=sql.Identifier(column_name)), {'row': row})
    single_row = cursor.fetchone()
    return single_row


def get_comment(col_value):
    return _get_single_row(col_value, 'comment')


def get_answer_by_id(answer_id):
    return _get_single_row(answer_id, 'answer')


def get_author_by_answer_id(answer_id):
    return get_answer_by_id(answer_id).get('user_id')


def get_question_by_id(question_id: int):
    return _get_single_row(question_id, 'question')


def get_author_id_by_question_id(question_id):
    return get_question_by_id(question_id).get('user_id')


@connection.connection_handler
def add_view(cursor, question_id):
    cursor.execute('''
                    UPDATE question
                    SET view_number = view_number + 1
                    WHERE id = %(id)s;
                    ''', {'id': question_id})


@connection.connection_handler
def vote_counter(cursor, question_id, user_id, table, direction):
    cursor.execute(
        sql.SQL(""" UPDATE  {table}
                       SET vote_number =
                       CASE
                       WHEN %(direction)s = 'up' THEN vote_number + 1
                       WHEN %(direction)s = 'down' THEN vote_number -1
                       END;
                       
                       UPDATE {table}
                       SET voted_users = %(user_id)s || voted_users
                       WHERE id = %(question_id)s;
                            """).format(table=sql.Identifier(table)),
        {'question_id': question_id,
         'table': table,
         'direction': direction,
         'user_id': user_id})


@connection.connection_handler
def edit_question(cursor, question_id, newdata):
    cursor.execute("""
                    UPDATE question
                    SET message = %(message)s
                    WHERE id = %(id)s;
                    """, {'message': newdata, 'id': question_id})


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
                    WHERE message ILIKE %(quote)s OR title ILIKE %(quote)s;
    ''', {'quote': '%' + quote + '%'})
    question_ids = cursor.fetchall()
    return question_ids


@connection.connection_handler
def search_answers(cursor, quote):
    cursor.execute('''
                    SELECT question_id FROM answer
                    WHERE message ILIKE %(quote)s;
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


@connection.connection_handler
def reputation(cursor, user_id, category):
    cursor.execute("""
                    UPDATE users
                    SET reputation = CASE 
                    WHEN %(category)s = 'question_vote' THEN reputation + 5
                    WHEN %(category)s = 'answer_vote' THEN reputation + 10
                    WHEN %(category)s = 'answer_accept' THEN reputation + 15
                    WHEN %(category)s = 'downvote' THEN reputation -2
                    END
                    WHERE users.id = %(id)s;   
    """, {'id': user_id,
          'category': category}
                   )


@connection.connection_handler
def get_user_id_by_username(cursor, username):
    cursor.execute("""
                    SELECT id FROM users
                    WHERE user_name = %(username)s 
    
    """, {'username': username})

    user_id = cursor.fetchone()
    return user_id['id']


@connection.connection_handler
def check_vote(cursor, table_name, user_id, question_id):
    cursor.execute(
        sql.SQL("""
                SELECT users.id FROM {table} JOIN users
                ON users.id = ANY (voted_users)
                WHERE {table}.id = %(question_id)s and users.id = %(user_id)s;
        """).format(table=sql.Identifier(table_name)), {
            'user_id': user_id,
            'question_id': question_id
        }
    )
    check_result = cursor.fetchall()
    if check_result == []:
        return True
    return False


@connection.connection_handler
def get_questions_for_comments(cursor, user_id):
    cursor.execute("""
    SELECT CASE WHEN comment.question_id IS NULL
    THEN a.question_id
  ELSE comment.question_id END,
       q.title  FROM comment
LEFT JOIN answer a ON comment.answer_id = a.id
  LEFT JOIN question q ON comment.question_id = q.id OR a.question_id = q.id
WHERE  comment.user_id= %(id)s;
     """, {"id": user_id})
    return cursor.fetchall()


@connection.connection_handler
def get_questions_for_question(cursor, user_id):
    cursor.execute("""
    SELECT id, title FROM question
WHERE  question.user_id =%(id)s;
""", {"id": user_id})
    return cursor.fetchall()


@connection.connection_handler
def get_questions_for_answers(cursor, user_id):
    cursor.execute("""
    SELECT q.id,q.title FROM answer a
INNER JOIN question q ON a.question_id = q.id
WHERE  a.user_id = %(id)s;
     """, {"id": user_id})
    return cursor.fetchall()



@connection.connection_handler
def update_accepted_answer(cursor, question_id, answer_id):
    cursor.execute("""
    UPDATE question
SET question.accepted_answer_id = %(a_id)s
WHERE question.id = %(q_id)s;
    """, {"q_id": question_id, "a_id": answer_id})

