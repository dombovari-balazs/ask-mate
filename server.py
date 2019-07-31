from flask import Flask, render_template, request, redirect, url_for, session, flash
import data_logic
import image_handler
import add_data
import app_objects
import security


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = image_handler.UPLOAD_FOLDER
app.secret_key = b'janesz'


@app.route('/')
def route_main():
    if 'user_name' in session:
        user = session['user_name']
    else:
        user = 'Senkise'
    latest = data_logic.get_all_rows('question', 'submission_time', 'desc', '5')
    return render_template('list.html', questions=latest, user=user)


@app.route('/image', methods=['GET', 'POST'])
def upload_image():
    return image_handler.upload_file()


@app.route('/list')
def route_list():
    return render_template('list.html', questions=data_logic.get_all_rows('question', 'submission_time',
                                                                          'asc'))


@app.route('/questions/<question_id>')
def display_question(question_id):
    data_logic.add_view(question_id)
    answers = data_logic.get_all_rows('answer', 'submission_time')
    comments = data_logic.get_all_rows('comment', 'submission_time')
    question = data_logic.get_single_row(question_id, 'question')
    return render_template("questions.html",
                           q_id=int(question_id),
                           answers=answers,
                           question=question,
                           comments=comments
                           )


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def add_answer(question_id):
    if request.method == 'POST':
        new_answer = request.form.get('new_answer')
        add_data.answer(question_id, new_answer)
        return redirect(url_for('display_question', question_id=question_id))
    return render_template("post-answer.html", q_id=question_id)


@app.route('/add_question', methods=['GET', 'POST'])
def route_add_question():
    if request.method == 'POST':
        username = data_logic.get_single_row(session['username'], 'users', 'user_name')
        question_id = add_data.question(request.form.get('title'), request.form.get('details'), username)
        return redirect(url_for('display_question', question_id=question_id))
    else:
        return render_template('add-question.html')


@app.route('/vote_up/<question_id>')
def vote_up(question_id):
    data_logic.vote_counter(question_id, 'up')
    return redirect('/questions/' + question_id)


@app.route('/vote_down/<question_id>')
def vote_down(question_id):
    data_logic.vote_counter(question_id, 'down')
    return redirect('/questions/' + question_id)


@app.route('/question/<question_id>/delete', methods=['GET', 'POST'])
def delete_question(question_id):
    data_logic.delete_all_comments(question_id=question_id)
    data_logic.delete_question_answers(question_id)
    data_logic.delete_data(question_id, 'question')
    return redirect('/')


@app.route('/answer/<question_id>/<answer_id>/delete', methods=['GET', 'POST'])
def delete_answer(answer_id, question_id):
    data_logic.delete_all_comments(answer_id=answer_id)
    data_logic.delete_data(answer_id, 'answer')
    return redirect("/questions/"+str(question_id))


@app.route('/answer/<question_id>/<answer_id>/edit', methods=['GET', 'POST'])
def edit_answer(answer_id, question_id):
    question = data_logic.get_single_row(question_id, 'question')
    answer = data_logic.get_single_row(answer_id, 'answer')
    if request.method == "GET":
        return render_template("edit-answer.html", answer=answer, question=question)
    else:
        data_logic.edit_answer(answer_id, request.form.get("edit_a"))
        return redirect("/questions/"+str(question_id))


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def edit(question_id):
    question = data_logic.get_single_row(question_id, 'question')
    if request.method == "GET":
        return render_template("edit.html", question=question)
    else:
        data_logic.edit_question(question_id, request.form.get("edit_q"))
        return redirect("/questions/"+str(question_id))


@app.route('/question/<question_id>/new-comment', methods=['GET', 'POST'])
def add_comment_question(question_id):
    if request.method == 'POST':
        message = request.form.get('message')
        add_data.comment(message, question_id)
        return redirect(url_for('display_question', question_id=question_id))
    else:
        specific_url = url_for('add_comment_question', question_id=question_id)
        return render_template('new-comment.html', question_id=question_id, specific_url=specific_url)


@app.route('/answer/<answer_id>/new-comment', methods=['GET', 'POST'])
def add_comment_answer(answer_id):
    if request.method == 'POST':
        message = request.form.get('message')
        question_id = data_logic.get_question_id(answer_id)
        data_logic.add_comment(message, question_id=question_id, answer_id=answer_id)
        return redirect(url_for('display_question', question_id=question_id))
    else:
        specific_url = url_for('add_comment_answer', answer_id=answer_id)
        return render_template('new-comment.html', answer_id=answer_id, specific_url=specific_url)


@app.route('/comments/<comment_id>/delete', methods=['POST', 'GET'])
def delete_comment(comment_id):
    question_id = data_logic.get_question_id(comment_id=comment_id)
    if request.method == 'GET':
        return render_template('confirm.html', comment_id=comment_id, question_id=question_id)
    else:
        data_logic.delete_data(comment_id, 'comments')
        return redirect(url_for('display_question', question_id=question_id))


@app.route('/comments/<comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(comment_id):
    if request.method == 'GET':
        comment = data_logic.get_one_comment(comment_id)
        return render_template('edit-comment.html', comment=comment)
    else:
        message = request.form.get('message')
        data_logic.edit_comment(comment_id=comment_id, message=message)
        question_id = data_logic.get_question_id(comment_id=comment_id)
        return redirect(url_for('display_question', question_id=question_id))


@app.route('/latest-questions')
def latest_questions():
    latest = data_logic.get_latest_questions()
    return render_template('list.html', dict=latest)


@app.route('/search')
def search_question():
    quote = request.args.get('q')
    question_ids = data_logic.convert_search_result(data_logic.search_questions(quote))
    answer_ids = data_logic.convert_search_result(data_logic.search_answers(quote))
    ids = question_ids | answer_ids
    questions = data_logic.question_search_result(list(ids))
    return render_template('list.html', questions=questions)


@app.route('/register', methods=['POST', 'GET'])
def route_register():
    form = app_objects.RegisterForm()
    if request.method == 'GET' and 'user_name' not in session:
        return render_template('register.html', form=form)
    elif 'user_name' in session:
        flash('lepj ki, cuni!', 'logged-in-error')
    elif request.method == 'POST':
        if form.validate_on_submit():
            add_data.registration(form.data)
            session['user_name'] = form.username.data
            return redirect(url_for('route_main'))
        else:
            return render_template('register.html', form=form)
    return redirect(url_for('route_main'))


@app.route('/login', methods=['POST', 'GET'])
def route_login():
    form = app_objects.LoginForm()
    login_error_class = 'active'
    if request.method == 'GET':
        login_error_class = 'hidden'
    elif request.method == 'POST' and form.validate_on_submit() and security.login(form.username.data, form.password.data):
        session['user_name'] = form.username.data
        return redirect(url_for('route_main'))
    return render_template('login.html', form=form, login_error_class=login_error_class)


@app.route('/logout')
def route_logout():
    session.pop('user_name', None)
    # session.pop('user_id', None)
    return redirect(url_for('route_main'))


if __name__ == "__main__":
    app.run()
