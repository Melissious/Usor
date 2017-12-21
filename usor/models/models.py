from bson import ObjectId
from bson.errors import InvalidId

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from mongoengine import (
    Q, StringField, DateTimeField, EmailField, BooleanField,
    IntField, ListField, ReferenceField, PULL, CASCADE
)

from ..common.helpers import random_string
from ..common.helpers import get_remote_addr, time_utcnow
from ..extentions import db


class Token(db.Document):
    meta = {
        "collection": "token",
        "indexes": [{
            "fields": ["data"],
        }]
    }
    data = StringField()
    expired = BooleanField(default=False)

    def __init__(self, data, reason=None, *args, **values):
        super(db.Document, self).__init__(*args, **values)
        self.data = data
        self.reason = reason

    def __repr__(self):
        return "<Token id: {}>".format(str(self.id))

    @property
    def has_expired(self):
        if self.expired:
            return True

    @classmethod
    def get(cls, data):
        return cls.objects(data=data).first()

    @classmethod
    def expire(cls, data):
        token = cls.get(data)
        if token:
            token.expired = True
            token.save()
        return token


class Role(db.Document):
    meta = {
        "collection": "role",
        "ordering": ["-create_at"],
        "indexes": [{
            "fields": ["name", "description"],
        }]
    }
    name = StringField(min_length=2, max_length=20, null=False, unique=True)
    description = StringField(max_length=160, null=False)
    create_at = DateTimeField(default=time_utcnow())
    update_at = DateTimeField(null=True)

    def __init__(self, name, description=None, *args, **values):
        super(db.Document, self).__init__(*args, **values)
        self.name = name
        self.description = description
        if self.description is None:
            self.description = self.name + " role"

    def __repr__(self):
        return "<Role {}, {}>".format(self.name, self.description[:60])

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
    def get(cls, role):
        try:
            return cls.objects(id=ObjectId(role)).get()
        except InvalidId:
            return cls.objects(name=role).first()


class User(db.Document, UserMixin):
    meta = {
        "collection": "user",
        "ordering": ["-create_at"],
        "indexes": [{
            "fields": ["username", "email"],
        }]
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

    roles = ListField(ReferenceField(Role, reverse_delete_rule=PULL))
    tokens = ListField(ReferenceField(Token, reverse_delete_rule=CASCADE))

    def __init__(self, username, email, password=None, *args, **values):
        super(db.Document, self).__init__(*args, **values)
        self.username = username
        self.email = email
        self.password = password

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

    @property
    def is_active(self):
        if self.email_verify:
            return True
        return False

    @classmethod
    def get(cls, login):
        try:
            return cls.objects(id=ObjectId(login)).get()
        except InvalidId:
            return cls.objects(Q(username=login) | Q(email=login)).first()

    @classmethod
    def authenticate(cls, login, password):
        user = cls.get(login)
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
            "access_token": token,
            "username": self.username,
            "email": self.email,
            "user_id": str(self.id),
            "user_roles": [role.name for role in self.roles]
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
