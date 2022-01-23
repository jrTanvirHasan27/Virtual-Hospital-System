from VirtualHospital import db, login_manager
from VirtualHospital import bcrypt
from flask_login import UserMixin, current_user


@login_manager.user_loader
def load_user(user_id):
    if int(user_id) >= 200:
        return Doctor.query.get(int(user_id))
    else:
        return Patients.query.get(int(user_id))


class Patients(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=80), unique=True, nullable=False)
    email_address = db.Column(db.String(length=100), unique=True, nullable=False)
    age = db.Column(db.Integer(), nullable=False)
    p_num = db.Column(db.String(length=13), unique=True, nullable=False)
    password_hash = db.Column(db.String(length=60), nullable=False)
    patient_budget = db.Column(db.Integer(), nullable=False, default=10000)
    owner_id = db.Column(db.Integer(), db.ForeignKey('doctor.id'))
    symptom = db.Column(db.String(length=1024), nullable=True)
    medication = db.Column(db.String(length=1024), nullable=True)
    dose = db.Column(db.String(length=2), nullable=True, default=None)
    feedback = db.Column(db.String(length=102), nullable=True, default=None)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def can_appoint(self, doctor):
        if current_user.owner_id is None and self.patient_budget >= doctor.priceOfAppointment:
            return True
        else:
            return False


class Doctor(db.Model, UserMixin):
    id = db.Column(db.Integer(), unique=True, nullable=False, primary_key=True)
    username = db.Column(db.String(length=80), unique=True, nullable=False)
    email = db.Column(db.String(length=100), unique=True, nullable=False)
    password_hash = db.Column(db.String(length=60), nullable=False)
    clas = db.Column(db.String(length=120), unique=False, nullable=False)
    qualification = db.Column(db.String(length=120), unique=False, default='M.B.B.S')
    experience = db.Column(db.String(length=50), unique=False, default=None)
    doctor_type = db.Column(db.String(length=200), unique=False, default=None)
    language = db.Column(db.String(length=500), unique=False, default='Bangla')
    phone_number = db.Column(db.String(length=14), unique=True, default=None)
    priceOfAppointment = db.Column(db.Integer(), unique=False, default=3000)
    patients = db.relationship('Patients', backref='owner')

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
