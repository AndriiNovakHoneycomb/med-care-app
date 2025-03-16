from backend.app import db
from backend.app.constants import UsersRoles
from backend.app.models import User, Patient, AuditLog, MedicalDocument
from datetime import datetime, date
from backend.app.sample_data.generate_samples import create_sample_documents
from backend.app.utils.storage import upload_file_to_s3
import uuid
import os

def seed_database():
    print("Starting database seeding...")
    
    # Check if admin user exists
    admin = User.query.filter_by(email='admin@admin.com').first()
    if not admin:
        admin = User(
            email='admin@admin.com',
            password='admin01',
            role=UsersRoles.ADMIN,
            first_name='super',
            last_name='admin',
            phone = '+380 93 11 111 11',
            status = 'Unapproved'
        )
        db.session.add(admin)
        print("Admin user created")
    else:
        print("Admin user already exists")

    # Create regular users and patients from the screenshot
    users_data = [
        {
            'email': 'brooklyn@gmail.com',
            'first_name': 'Janny',
            'last_name': 'Smith',
            'password': 'password123',
            'role': UsersRoles.PATIENT,
            'phone': '+380 93 11 111 11',
            'status': 'Unapproved',
            'patient': {
                'dob': date(1990, 1, 1),
                'phone': '+1 (406) 555-0120'
            }
        },
        {
            'email': 'jacob@gmail.com',
            'first_name': 'Aaron',
            'last_name': 'Brant',
            'password': 'password123',
            'role': UsersRoles.PATIENT,
            'phone': '+380 93 11 111 11',
            'status': 'Unapproved',
            'patient': {
                'dob': date(1985, 1, 1),
                'phone': '+1 (406) 555-0120'
            }
        },
        {
            'email': 'darrell@gmail.com',
            'first_name': 'Ron',
            'last_name': 'Cooper',
            'password': 'password123',
            'role': UsersRoles.PATIENT,
            'phone': '+380 93 11 111 11',
            'status': 'Unapproved',
            'patient': {
                'dob': date(1988, 1, 1),
                'phone': '+1 (406) 555-0120'
            }
        },
        {
            'email': 'jerome@gmail.com',
            'first_name': 'Esther',
            'last_name': 'Howard',
            'password': 'password123',
            'role': UsersRoles.PATIENT,
            'phone': '+380 93 11 111 11',
            'status': 'Unapproved',
            'patient': {
                'dob': date(1992, 1, 1),
                'phone': '+1 (406) 555-0120'
            }
        },
        {
            'email': 'esther@gmail.com',
            'first_name': 'Ronald',
            'last_name': 'Richards',
            'password': 'password123',
            'role': UsersRoles.PATIENT,
            'phone': '+380 93 11 111 11',
            'status': 'Unapproved',
            'patient': {
                'dob': date(1987, 1, 1),
                'phone': '+1 (406) 555-0120'
            }
        },
        {
            'email': 'janeco@gmail.com',
            'first_name': 'Jerome',
            'last_name': 'Bell',
            'password': 'password123',
            'role': UsersRoles.PATIENT,
            'phone': '+380 93 11 111 11',
            'status': 'Unapproved',
            'patient': {
                'dob': date(1991, 1, 1),
                'phone': '+1 (406) 555-0120'
            }
        },
        {
            'email': 'cameron@gmail.com',
            'first_name': 'Brooklyn',
            'last_name': 'Simmons',
            'password': 'password123',
            'role': UsersRoles.PATIENT,
            'phone': '+380 93 11 111 11',
            'status': 'Unapproved',
            'patient': {
                'dob': date(1989, 1, 1),
                'phone': '+1 (406) 555-0120'
            }
        },
        {
            'email': 'kristinwa@gmail.com',
            'first_name': 'Marvin',
            'last_name': 'McKinney',
            'password': 'password123',
            'role': UsersRoles.PATIENT,
            'phone': '+380 93 11 111 11',
            'status': 'Unapproved',
            'patient': {
                'dob': date(1986, 1, 1),
                'phone': '+1 (406) 555-0120'
            }
        }
    ]

    # Generate sample medical documents
    print("Generating sample medical documents...")
    sample_documents = create_sample_documents()

    created_patients = []
    for user_data in users_data:
        # Check if user exists
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if existing_user:
            print(f"User {user_data['email']} already exists")
            existing_patient = Patient.query.filter_by(user_id=existing_user.id).first()
            if existing_patient:
                created_patients.append(existing_patient)
            continue

        user = User(
            email=user_data['email'],
            password=user_data['password'],
            role=user_data['role'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone=user_data['phone'],
            status=user_data['status'],
        )
        db.session.add(user)
        db.session.flush()  # This will assign the ID to the user

        patient_data = user_data['patient']
        patient = Patient(
            user_id=user.id,
            dob=patient_data['dob']
        )
        db.session.add(patient)
        created_patients.append(patient)

        # Create an audit log for the new patient
        audit_log = AuditLog(
            user_id=user.id,
            action=f"Patient account created for {user_data['first_name']} {user_data['last_name']}",
            details={
                'event': 'patient_created',
                'patient_name': f"{user_data['first_name']} {user_data['last_name']}",
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        db.session.add(audit_log)
        print(f"Created user and patient for {user_data['email']}")

    # Commit to get patient IDs
    db.session.commit()

    print("Adding medical documents to patients...")
    # Distribute sample documents among patients
    for i, patient in enumerate(created_patients):
        # Check if patient already has documents
        existing_docs = MedicalDocument.query.filter_by(patient_id=patient.id).count()
        if existing_docs > 0:
            print(f"Patient {patient.user.email} already has documents")
            continue

        # Each patient gets all types of documents
        for doc_info in sample_documents:
            try:
                # Generate unique filename
                file_extension = os.path.splitext(doc_info['path'])[1]
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                
                # Upload to S3
                with open(doc_info['path'], 'rb') as file:
                    s3_path = upload_file_to_s3(file, unique_filename)
                
                # Create document record
                document = MedicalDocument(
                    patient_id=patient.id,
                    title=f"{doc_info['title']} - {patient.user.first_name} {patient.user.last_name}",
                    file_path=s3_path
                )
                db.session.add(document)
                
                # Create audit log
                audit_log = AuditLog(
                    user_id=patient.user_id,
                    action=f"Medical document uploaded during seeding",
                    details={
                        'document_type': doc_info['type'],
                        'document_title': document.title,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                )
                db.session.add(audit_log)
                
                print(f"Added {doc_info['title']} for patient {patient.user.first_name} {patient.user.last_name}")
                
            except Exception as e:
                print(f"Error uploading document: {str(e)}")
                continue

    try:
        db.session.commit()
        print("Database seeded successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding database: {str(e)}")
        raise

if __name__ == '__main__':
    seed_database() 