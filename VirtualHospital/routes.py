from VirtualHospital import app
from flask import render_template, redirect, url_for, flash, request
from VirtualHospital.models import Doctor, Patients
from VirtualHospital.forms import SignUpForm, DoctorSignUpForm, SignInForm, SignInFormDoctor, TakeAppointmentForm, \
    EditAppointmentInfoForm, RemovePatientForm, UpdateMedicationForm, GiveFeedBackOption
from VirtualHospital import db
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/home')
@login_required
def home_page():
    return render_template('home.html')


@app.route('/homeD')
@login_required
def homeD_page():
    return render_template('homeD.html')


@app.route('/FAQ')
@login_required
def Faq_page():
    return render_template('FAQ.html')


@app.route('/ViewFeedback')
@login_required
def ViewFeedback_page():
    appointed_patient = Patients.query.filter_by(owner_id=current_user.id)
    return render_template('ViewFeedback.html', appointed_patient=appointed_patient)


@app.route('/GiveFeedback', methods=['GET', 'POST'])
@login_required
def Give_feedback():
    feedBackForm = GiveFeedBackOption()
    if request.method == 'POST':
        if feedBackForm.validate_on_submit():
            current_user.feedback = feedBackForm.feedback.data
            db.session.commit()
            flash(f'Congratulations, {current_user.username} You have successfully updated your feedback!', category='success')
            return redirect(url_for('Give_feedback'))

    if request.method == 'GET':
        return render_template('giveFeedback.html', feedBackForm=feedBackForm)


@app.route('/UpdateMedication', methods=['GET', 'POST'])
@login_required
def Update_medication():
    selectForm = UpdateMedicationForm()
    selected_patient = request.form.get('patient_select')
    if request.method == "POST":
        patient_to_update = Patients.query.filter_by(username=selected_patient).first()
        if patient_to_update:
            if selectForm.validate_on_submit():
                patient_to_update.medication = selectForm.medication.data
                patient_to_update.dose = selectForm.dose.data
                db.session.commit()
                flash(f"You have successfully updated {patient_to_update.username}'s medication!", category='success')
                return redirect(url_for('homeD_page'))

    if request.method == "GET":
        patientList = Patients.query.filter_by(owner_id=current_user.id)
        return render_template('UpdateMedication.html', patientList=patientList, selectForm=selectForm)


@app.route('/RemovePatient', methods=['GET', 'POST'])
@login_required
def RemovePatient():
    removePatientForm = RemovePatientForm()
    if request.method == "POST":
        appointed_patient = request.form.get('appointed_patient')
        a_patient_object = Patients.query.filter_by(username=appointed_patient).first()
        if a_patient_object:
            if a_patient_object.owner_id == current_user.id:
                a_patient_object.owner_id = None
                a_patient_object.medication = None
                a_patient_object.dose = None
                a_patient_object.symptom = None
                a_patient_object.feedback = None
                db.session.commit()
                flash(f'{a_patient_object.username} Has Been Removed successfully from your appointed patient list!!',
                      category='success')
            return redirect(url_for('RemovePatient'))

    if request.method == "GET":
        appointed_patients = Patients.query.filter_by(owner_id=current_user.id)
        return render_template('RemovePatient.html', appointed_patients=appointed_patients,
                               removePatientForm=removePatientForm)


@app.route('/PatientList', methods=['GET', 'POST'])
@login_required
def Patient_List():
    if request.method == "GET":
        appointed_patients = Patients.query.filter_by(owner_id=current_user.id)
        return render_template('appointed_patientList.html', appointed_patients=appointed_patients)


@app.route('/AppointmentInfo', methods=['GET', 'POST'])
@login_required
def appointment_information():
    appoint_info = EditAppointmentInfoForm()
    if request.method == "POST":
        if appoint_info.validate_on_submit():
            current_user.symptom = appoint_info.symptom.data
            db.session.commit()
            flash(f'You have successfully updated your appointment information!', category='success')
            return redirect(url_for('appointment_information'))

    if request.method == "GET":
        return render_template('Appointment_info.html', appoint_info=appoint_info)


@app.route('/Doctors', methods=['GET', 'POST'])
def Appointment_Doctors():
    appointment_form = TakeAppointmentForm()
    if request.method == "POST":
        appointed_doctor = request.form.get('appointed_doctor')
        a_doctor_object = Doctor.query.filter_by(username=appointed_doctor).first()
        if a_doctor_object:
            if current_user.can_appoint(a_doctor_object):
                current_user.owner_id = a_doctor_object.id
                current_user.patient_budget -= a_doctor_object.priceOfAppointment
                db.session.commit()
                flash(
                    f'Congratulations! You have appointed Dr. {a_doctor_object.username} for {a_doctor_object.priceOfAppointment} BDT. Now please update the necessary information.',
                    category='success')
                return redirect(url_for('appointment_information'))
            else:
                flash(
                    f"Either you already had appointed a doctor or you don't have enough money to appoint Dr. {a_doctor_object.username}!",
                    category='danger')
                return redirect(url_for('Appointment_Doctors'))

    if request.method == "GET":
        doctors = Doctor.query.all()
        return render_template('Appointment.html', doctors=doctors, appointment_form=appointment_form)


@app.route('/AvailableDoctors')
@login_required
def Available_Doctors():
    Doctors = Doctor.query.all()
    return render_template('Available_doctors.html', Doctors=Doctors)


@app.route('/')
@app.route('/welcome')
def welcome_page():
    return render_template('welcome.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    form = SignUpForm()
    if form.validate_on_submit():
        patient_to_create = Patients(username=form.username.data,
                                     age=form.age.data,
                                     email_address=form.email_address.data,
                                     p_num=form.p_num.data,
                                     password=form.password1.data)
        db.session.add(patient_to_create)
        db.session.commit()
        flash(f'Congratulations {patient_to_create.username}! you have successfully created your account.',
              category='success')
        return redirect(url_for('signin_patient_page'))
    if form.errors != {}:  # if there are no errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a patient user: {err_msg}', category='danger')
    return render_template('signup.html', form=form)


@app.route('/DoctorSignup', methods=['GET', 'POST'])
def doctor_signup_page():
    form = DoctorSignUpForm()
    if form.validate_on_submit():
        doctor_to_create = Doctor(id=form.id.data,
                                  username=form.username.data,
                                  email=form.email.data,
                                  clas=form.clas.data,
                                  password=form.password1.data,
                                  experience=form.experience.data,
                                  phone_number=form.phone_number.data
                                  )
        db.session.add(doctor_to_create)
        db.session.commit()
        flash(f'Congratulations {doctor_to_create.username}! you have successfully created your account.',
              category='success')
        return redirect(url_for('signin_doctor_page'))
    if form.errors != {}:  # if there are no errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error creating a doctor user: {err_msg}', category='danger')
    return render_template('signupD.html', form=form)


@app.route('/signin', methods=['GET', 'POST'])
def signin_patient_page():
    form = SignInForm()
    if form.validate_on_submit():
        attempted_patient = Patients.query.filter_by(username=form.username.data).first()
        if attempted_patient and attempted_patient.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_patient)
            flash(f'You are successfully logged in as {attempted_patient.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username and password are not matched! Please try again', category='danger')

    return render_template('signin.html', form=form)


@app.route('/DoctorSignin', methods=['GET', 'POST'])
def signin_doctor_page():
    form = SignInFormDoctor()
    if form.validate_on_submit():
        attempted_Doctor = Doctor.query.filter_by(username=form.username.data).first()
        if attempted_Doctor and attempted_Doctor.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_Doctor)
            flash(f'You are successfully logged in as {attempted_Doctor.username}', category='success')
            return redirect(url_for('homeD_page'))
        else:
            flash('Username and password are not matched! Please try again', category='danger')
    return render_template('signinD.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out successfully!", category='info')
    return redirect(url_for('welcome_page'))


@app.route('/aboutUs')
@login_required
def about_Us_page():
    return render_template('AboutUs.html')


@app.route('/doctorProfile')
def doctor_profile_page():
    return render_template('Doctor_Profile.html')


@app.route('/patientProfile')
def patient_profile_page():
    return render_template('Patient_Profile.html')
