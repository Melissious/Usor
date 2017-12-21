from dns import resolver
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import Length

from ..models.models import User, Role
from ..extentions import ma


def used_data(data):
    if User.get(data):
        raise ValidationError("already use.")


def data_required(data):
    if not data:
        raise ValidationError('data required.')


class LoginSchema(ma.Schema):
    login = fields.String(required=True, validate=data_required)

    @validates
    def validate_login(self, login):
        if not User.get(login):
            raise ValidationError('user not found')

    class Meta:
        ordered = True


class RoleSchema(LoginSchema):
    description = fields.String(validate=[Length(max=120)])
    role = fields.String(required=True, validate=[data_required, Length(min=2, max=20)])

    class Meta:
        model = Role


class UserSchema(LoginSchema):
    username = fields.String(required=True, validate=[Length(min=4, max=24), used_data])
    email = fields.Email(required=True, validate=[data_required, used_data])
    password = fields.String(required=True, validate=data_required)

    new_password = fields.String(required=True, validate=data_required)
    old_password = fields.String(required=True, validate=data_required)
    token = fields.String(required=True, validate=data_required)

    @validates
    def validate_role(self, role):
        if not Role.get(role):
            raise ValidationError('role not found')

    @validates
    def validate_email(self, email):
        if "@" in email:
            email_hostname = email.split("@")[1]
            try:
                resolver.query(email_hostname, "MX")
            # is not an email server or email domain name is not register
            except (resolver.NoAnswer, resolver.NXDOMAIN) as e:
                raise ValidationError("invalid email hostname.")
            # network error
            except (resolver.Timeout, resolver.NoNameservers) as e:
                raise ValidationError("network error.")

    class Meta:
        model = User
        model_fields_kwargs = {'_password': {'load_only': True}}
