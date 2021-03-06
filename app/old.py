@app.route('/restorePassword', methods=['GET', 'POST'])
def restore_password_welcome():
    form = RestorePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash('Incorrect username', category='alert-danger')
            return redirect(url_for('restore_password_welcome'))
        current_time = datetime.utcnow().replace(microsecond=0)
        code = strgen.StringGenerator('[0-9]{10}').render()
        restore_token = RestoreToken(user=user, code=code, time=current_time)
        send_verification_code(user.email, user.first_name, code)
        db.session.commit()
        return redirect(url_for('restore_password_selected', username=user.username))
    return render_template('restore_password.html', title='Restore password', form=form)


@app.route('/restorePassword/<username>', methods=['GET', 'POST'])
def restore_password_selected(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = VerificationCodeForm()
    if form.validate_on_submit():
        code = form.code.data
        restore_token = RestoreToken.get_token(user)
        if restore_token is None:
            flash('Error while finding selected user', category='alert-danger')
            return redirect(url_for('restore_password_welcome'))
        if code != restore_token.code:
            flash('Code is incorrect, try again', category='alert-danger')
            return redirect(url_for('restore_password_selected', username=username))
        new_password = strgen.StringGenerator('[\w\d]{16}').render()
        user.set_password(new_password)
        send_new_password(user.email, user.first_name, new_password)
        db.session.commit()
        flash('New password has been sent to you by email', category='alert-success')
        return redirect(url_for('logout'))
    return render_template('verify.html', title='Restore password', form=form, user=user)


@app.route('/changePassword', methods=['GET', 'POST'])
@login_required
def change_password():
    form = EditPasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash('Incorrect password', category='alert-danger')
            return redirect(url_for('change_password'))
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Password has been successfully changed', category='alert-success')
        return redirect(url_for('logout'))
    return render_template('change_password.html', title='Change password', form=form)


@app.route('/user/<username>')
def profile_page(username):
    user = User.query.filter_by(username=username).first_or_404()
    avatar_form = EditAvatarForm()
    profile_form = EditProfileForm(user.email)
    return render_template('user.html', title='View profile', user=user, 
        avatar_form=avatar_form, profile_form=profile_form)


@app.route('/avatars/<filename>')
def avatar(filename):
    return send_from_directory(app.config['AVATARS_SAVE_PATH'], filename)


@app.route('/changeAvatar', methods=['POST'])
@login_required
def change_avatar():
    form = EditAvatarForm()
    if form.validate_on_submit():
        filename = avatars.save_avatar(form.image.data)
        current_user.avatar = filename
        db.session.commit()
        flash('Your avatar has been saved', category='alert-success')
    else:
        flash('Data is incorrect', category='alert-danger')
    return redirect(url_for('profile_page', username=current_user.username))


@app.route('/changeProfile', methods=['POST'])
@login_required
def change_profile():
    form = EditProfileForm(current_user.email)
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your information has been saved', category='alert-success')
    else:
        flash('Data is incorrect', category='alert-danger')
    return redirect(url_for('profile_page', username=current_user.username))


@app.route('/download/submission/<submission_id>')
@login_required
def download_submission(submission_id):
    submission = Submission.query.filter_by(id=submission_id).first_or_404()
    if submission.user != current_user:
        flash('Forbidden operation', category='alert-danger')
        return redirect(url_for('contests_page'))
    source = submission.source
    download_folder = app.config['SUBMISSIONS_DOWNLOAD_PATH']
    filename = str(submission_id).zfill(6) + '.' + submission.language
    path = os.path.join(download_folder, filename)
    open(path, 'w').write(source)
    return send_from_directory(download_folder, filename, as_attachment=True)


@app.route('/contests/<contest_id>/<number>/main/send', methods=['POST'])
@login_required
def send(contest_id, number):
    contest = get_contest_by_id(contest_id)
    contest_request = get_contest_request(contest)
    problem = Problem.query.filter_by(contest=contest, number=number).first_or_404()
    try:
        if contest_request is None or contest_request.state() != 'In progress':
            raise ValueError('You are not allowed to send submissions in this contest')
        if problem.problem_type == 'Programming':
            problem_form = FileProblemForm()
            if not problem_form.validate_on_submit():
                raise ValueError('Form is not valid')
            language = problem_form.language.data
            source = problem_form.source.data.read().decode('utf-8')
            current_time = datetime.utcnow().replace(microsecond=0)
            submission = Submission(contest=contest, problem=problem, user=current_user, time=current_time, 
                language=language, status='In queue', score=0, source=source)
            current_user.active_language = language
            db.session.add(submission)
            db.session.commit()
            submit_to_queue(group='invokers', obj={
                'type': 'evaluate',
                'submission_id': submission.id
            })
            flash('Your solution has been sent', category='alert-success')
    except ValueError as error:
        flash('Submission error: ' + str(error), category='alert-danger')
    return redirect(url_for('load_problem', contest_id=contest.id, number=number, attr='main'))


@app.route('/contests/<contest_id>/finish')
@login_required
def finish_contest(contest_id):
    contest = get_contest_by_id(contest_id)
    contest_request = get_contest_request(contest)
    if contest_request is None or contest_request.state() in ['Not started', 'Finished']:
        flash('Forbidden operation', category='alert-danger')
        return redirect(url_for('contests_page'))
    current_time = datetime.utcnow().replace(microsecond=0)
    contest_request.finish_time = current_time
    db.session.commit()
    return redirect(url_for('load_problem', contest_id=contest.id, number=1, attr='main'))


# if contest_request.state() == 'Finished':
#     flash('Ваше участие в контесте завершено', category='alert-info')
# if problem.problem_type == 'Programming':
#     problem_form = FileProblemForm(language=current_user.active_language)
#     return render_template('contest_problem_prog.html', title=contest.name, contest=contest,
#         problem=problem, problem_manager=problem_manager, request=contest_request,
#         submissions=submissions, form=problem_form)
# elif problem.problem_type == 'Test':
#     problem_form = InputProblemForm()
#     return render_template('contest_problem_test.html', title=contest.name, contest=contest,
#         problem=problem, request=contest_request, submissions=submissions, form=problem_form)


@app.route('/contests/<contest_id>/admin', methods=['GET', 'POST'])
@app.route('/contests/<contest_id>/admin/info', methods=['GET', 'POST'])
@login_required
@contest_admin
def contest_admin_info(contest_id):
    contest = get_contest_by_id(contest_id)
    info_form = AdminInfoForm(contest.name, contest_type=contest.contest_type)
    if info_form.validate_on_submit():
        contest.name = info_form.name.data
        contest.contest_type = info_form.contest_type.data
        contest.duration = timedelta(minutes=info_form.duration.data)
        db.session.commit()
        flash('Contest info has been saved', category='alert-success')
    return render_template('contest_admin_info.html', title=contest.name, contest=contest, form=info_form)


@app.route('/contests/<contest_id>/admin/problems')
@login_required
@contest_admin
def contest_admin_problems(contest_id):
    contest = get_contest_by_id(contest_id)
    return render_template('contest_admin_problems.html', title=contest.name, contest=contest)


@app.route('/contests/<contest_id>/admin/participants')
@login_required
@contest_admin
def contest_admin_participants(contest_id):
    contest = get_contest_by_id(contest_id)
    return render_template('contest_admin_participants.html', title=contest.name, contest=contest)


@app.route('/contests/<contest_id>/admin/submissions')
@login_required
@contest_admin
def contest_admin_submissions(contest_id):
    contest = get_contest_by_id(contest_id)
    return render_template('contest_admin_submissions.html', title=contest.name, contest=contest)


@app.route('/contests/<contest_id>/admin/notifications')
@login_required
@contest_admin
def contest_admin_notifications(contest_id):
    contest = get_contest_by_id(contest_id)
    return render_template('contest_admin_notifications.html', title=contest.name, contest=contest)
