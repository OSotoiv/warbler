"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py

from unittest import TestCase
from models import db, User, Message, Likes
from forms import UserUpdateForm, UserAddForm
from sqlalchemy.exc import IntegrityError

import os
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler-test'
from app import app
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()


class MessageModelTestCase(TestCase):
    """Test model for Message."""

    def setUp(self):
        """Create test client, add sample data"""
        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        user = User(
            email="setup@setup.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
        db.session.add(user)
        db.session.commit()
        self.user = user

        msg = Message(
            text='Warblers are bright and beautiful songbirds, known for their distinctive TWEETS')
        user.messages.append(msg)
        db.session.add(msg)
        db.session.commit()
        self.msg = msg
        self.msg_id = msg.id

    def test_message_model_creation(self):
        """Test basic model"""
        # at this point user has only one message
        self.assertEqual(len(self.user.messages), 1)
        # message should always have only one user
        self.assertEqual(self.msg.user.id, self.user.id)

    def test_many_messages_1_user(self):
        """test many Messages to one User"""
        msg2 = Message(
            text='Here is a 2nd message')
        self.user.messages.append(msg2)
        db.session.add(msg2)
        db.session.commit()
        msg3 = Message(
            text='We should now have 3 messages')
        self.user.messages.append(msg3)
        db.session.add(msg3)
        db.session.commit()

        self.assertEqual(len(self.user.messages), 3)

    def test_msg_like_table(self):
        """test likes msg table connection"""
        other_user = User(
            email="other_user@connect.com",
            username="test_other_user",
            password="HASHED_PASSWORD2"
        )
        db.session.add(other_user)
        db.session.commit()
        message = Message.query.get_or_404(self.msg_id)
        other_user.likes.append(message)
        db.session.commit()
        # like = Likes.query.filter_by(message_id=self.msg_id).first()
        # import pdb
        # pdb.set_trace()
        # other user has no messages
        self.assertEqual(len(other_user.messages), 0)
        # other user has one liked message from self.user
        self.assertEqual(len(other_user.likes), 1)
        # at this point only one like exist
        self.assertEqual(len(Likes.query.all()), 1)
        # deleting a user also removes messages and likes
        db.session.delete(self.user)
        db.session.commit()

        # other_user should now have no likes
        self.assertEqual(len(other_user.likes), 0)
        # at this point no Likes should exist
        self.assertEqual(len(Likes.query.all()), 0)

    # def test_delete_msg_cascade(self):
