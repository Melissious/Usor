from bson import ObjectId
from bson.errors import InvalidId

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from mongoengine import (
    Q, StringField, DateTimeField, EmailField, BooleanField,
    IntField, ListField, ReferenceField, PULL
)

from ..common.helpers import random_string
from ..extentions import db
from ..common.helpers import get_remote_addr, time_utcnow


class Role(db.Document):
    meta = {
        'collection': 'role',
        'ordering': ['-create_at']
    }
    name = StringField(
        min_length=2, max_length=20, null=False, unique=True
    )
    description = StringField(max_length=160, null=False)
    create_at = DateTimeField(default=time_utcnow())
    update_at = DateTimeField(null=True)

    def __init__(self, name, description=None, *args, **values):
        super(db.Document, self).__init__(*args, **values)
        self.name = name
        self.description = description
        if self.description is None:
            self.description = self.name + " role"

    def to_dict(self, tracking=False):
        data = {
            "role": self.name,
            "description": self.description
        }
        if tracking:
            data.update({
                "role_id": str(self.id),
                "create_at": self.create_at,
                "update_at": self.update_at
            })
        return data

    @classmethod
    def get_role(cls, role):
        try:
            return cls.objects(id=ObjectId(role)).get()
        except InvalidId:
            return cls.objects(name=role).first()


class User(db.Document, UserMixin):
    meta = {
        'collection': 'user',
        'ordering': ['-create_at']
    }
    username = StringField(
        required=True, min_length=3,
        max_length=20, null=False, unique=True
    )
    email = EmailField(
        required=True, max_length=120,
        null=False, unique=True
    )
    _password = StringField(required=True, null=False)

    email_verify = BooleanField(default=False)
    activate = BooleanField(default=False)
    access = BooleanField(default=True)

    create_at = DateTimeField(default=time_utcnow())
    update_at = DateTimeField(null=True)
    logged_at = DateTimeField(null=True)
    logged_ip = StringField(max_length=50, null=True)
    login_counter = IntField(default=0)
    _sid = StringField(max_length=42, null=False)

    roles = ListField(
        ReferenceField(Role, reverse_delete_rule=PULL)
    )

    def __init__(self, username, email, password=None, *args, **values):
        super(db.Document, self).__init__(*args, **values)
        self.username = username
        self.email = email
        self.password = password

    def __unicode__(self):
        return str(self.id)

    def __repr__(self):
        return "<User {}, {}>".format(self.username, self.email)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        if not password:
            return
        self._password = generate_password_hash(password)

    password = property(_get_password, _set_password)

    def check_password(self, password):
        if self._password is None:
            return False
        return check_password_hash(self._password, password)

    def _get_sid(self):
        return self._sid

    def _set_sid(self, unique_string):
        self._sid = unique_string

    sid = property(_get_sid, _set_sid)

    @property
    def is_active(self):
        if self.email_verify:
            return True
        return False

    @classmethod
    def get_user(cls, login):
        try:
            return cls.objects(id=ObjectId(login)).get()
        except InvalidId:
            return cls.objects(Q(username=login) | Q(email=login)).first()

    @classmethod
    def authenticate(cls, login, password):
        user = cls.get_user(login)
        if user and user.check_password(password):
            user.login_counter += 1
            user.logged_at = time_utcnow()
            user.logged_ip = get_remote_addr()
            user.save()
            return user
        # protection against account enumeration timing attacks
        check_password_hash(random_string(10), password)

    def to_dict(self, token=None, tracking=False):
        data = {
            "auth_token": token,
            "username": self.username,
            "email": self.email,
            "usor_id": str(self.id),
            "usor_roles": [role.name for role in self.roles]
        }
        if tracking:
            data.update({
                "activate": self.activate,
                "access": self.access,
                "create_at": self.create_at,
                "update_at": self.update_at,
                "logget_at": self.logged_at,
                "logget_ip": self.logged_ip,
                "login_counter": self.login_counter
            })
        return data
