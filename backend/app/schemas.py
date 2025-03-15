from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime
from backend.app.constants import UsersRoles

class UserSchema(Schema):
    id = fields.UUID(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True, validate=validate.Length(min=8))
    role = fields.Str(required=True, validate=validate.OneOf([
        UsersRoles.ADMIN,
        UsersRoles.STAFF,
        UsersRoles.PATIENT
    ]))
    created_at = fields.DateTime(dump_only=True)

class PatientSchema(Schema):
    id = fields.UUID(dump_only=True)
    user_id = fields.UUID(dump_only=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=1))
    last_name = fields.Str(required=True, validate=validate.Length(min=1))
    dob = fields.Date(required=True)
    created_at = fields.DateTime(dump_only=True)
    
    @validates('dob')
    def validate_dob(self, value):
        if value > datetime.now().date():
            raise ValidationError('Date of birth cannot be in the future')

class MedicalDocumentSchema(Schema):
    id = fields.UUID(dump_only=True)
    patient_id = fields.UUID(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    file_path = fields.Str(dump_only=True)
    summary = fields.Str()
    uploaded_at = fields.DateTime(dump_only=True)

class AuditLogSchema(Schema):
    id = fields.UUID(dump_only=True)
    user_id = fields.UUID(dump_only=True)
    action = fields.Str(required=True)
    timestamp = fields.DateTime(dump_only=True)
    details = fields.Dict(keys=fields.Str(), values=fields.Raw())

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class TokenSchema(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()

# Initialize schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)
patient_schema = PatientSchema()
patients_schema = PatientSchema(many=True)
medical_document_schema = MedicalDocumentSchema()
medical_documents_schema = MedicalDocumentSchema(many=True)
audit_log_schema = AuditLogSchema()
audit_logs_schema = AuditLogSchema(many=True)
login_schema = LoginSchema()
token_schema = TokenSchema() 