from app import db
from app.models import User, Patient, AuditLog
from datetime import datetime, date

def seed_database():
    print("Starting database seeding...")
    
    # Create admin user
    admin = User(
        email='admin@admin.com',
        password='admin01',
        role='admin'
    )
    db.session.add(admin)
    print("Admin user created")

    # Create regular users and patients from the screenshot
    users_data = [
        {
            'email': 'brooklyn@gmail.com',
            'password': 'password123',
            'role': 'patient',
            'patient': {
                'first_name': 'Janny',
                'last_name': 'Smith',
                'dob': date(1990, 1, 1),  # Example date
                'phone': '+1 (406) 555-0120'
            }
        },
        {
            'email': 'jacob@gmail.com',
            'password': 'password123',
            'role': 'patient',
            'patient': {
                'first_name': 'Aaron',
                'last_name': 'Brant',
                'dob': date(1985, 1, 1),
                'phone': '+1 (406) 555-0120'
            }
        },
        {
            'email': 'darrell@gmail.com',
            'password': 'password123',
            'role': 'patient',
            'patient': {
                'first_name': 'Ron',
                'last_name': 'Cooper',
                'dob': date(1988, 1, 1),
                'phone': '+1 (406) 555-0120'
            }
        },
        {
            'email': 'jerome@gmail.com',
            'password': 'password123',
            'role': 'patient',
            'patient': {
                'first_name': 'Esther',
                'last_name': 'Howard',
                'dob': date(1992, 1, 1),
                'phone': '+1 (406) 555-0120'
            }
        },
        {
            'email': 'esther@gmail.com',
            'password': 'password123',
            'role': 'patient',
            'patient': {
                'first_name': 'Ronald',
                'last_name': 'Richards',
                'dob': date(1987, 1, 1),
                'phone': '+1 (406) 555-0120'
            }
        },
        {
            'email': 'janeco@gmail.com',
            'password': 'password123',
            'role': 'patient',
            'patient': {
                'first_name': 'Jerome',
                'last_name': 'Bell',
                'dob': date(1991, 1, 1),
                'phone': '+1 (406) 555-0120'
            }
        },
        {
            'email': 'cameron@gmail.com',
            'password': 'password123',
            'role': 'patient',
            'patient': {
                'first_name': 'Brooklyn',
                'last_name': 'Simmons',
                'dob': date(1989, 1, 1),
                'phone': '+1 (406) 555-0120'
            }
        },
        {
            'email': 'kristinwa@gmail.com',
            'password': 'password123',
            'role': 'patient',
            'patient': {
                'first_name': 'Marvin',
                'last_name': 'McKinney',
                'dob': date(1986, 1, 1),
                'phone': '+1 (406) 555-0120'
            }
        }
    ]

    for user_data in users_data:
        user = User(
            email=user_data['email'],
            password=user_data['password'],
            role=user_data['role']
        )
        db.session.add(user)
        db.session.flush()  # This will assign the ID to the user

        patient_data = user_data['patient']
        patient = Patient(
            user_id=user.id,
            first_name=patient_data['first_name'],
            last_name=patient_data['last_name'],
            dob=patient_data['dob']
        )
        db.session.add(patient)

        # Create an audit log for the new patient
        audit_log = AuditLog(
            user_id=user.id,
            action=f"Patient account created for {patient_data['first_name']} {patient_data['last_name']}",
            details={
                'event': 'patient_created',
                'patient_name': f"{patient_data['first_name']} {patient_data['last_name']}",
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        db.session.add(audit_log)

    try:
        db.session.commit()
        print("Database seeded successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding database: {str(e)}")
        raise

if __name__ == '__main__':
    seed_database() 