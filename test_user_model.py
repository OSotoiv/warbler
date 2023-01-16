"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

from app import app
from sqlalchemy.exc import IntegrityError
from forms import UserUpdateForm, UserAddForm
from models import db, User, Message
from unittest import TestCase
import os
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler-test'
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False


# Now we can import app
# >>>>>>>>>this is not working for me. vsCode keeps moving import app to the top when i save
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test model for User."""

    def setUp(self):
        """Create test client, add sample data."""

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

    def test_user_model_creation(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages,followers or likes
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.following), 0)
        self.assertEqual(len(u.likes), 0)
        self.assertFalse(u.is_followed_by(self.user.id))
        self.assertFalse(u.is_following(self.user.id))
        # db.session.delete(u)
        # db.session.commit()

    def test_user_model_update(self):
        """User model method `User.update(pass in form here)` to update a user"""
        # befor update
        self.assertEqual(self.user.username, "testuser1")
        self.assertEqual(self.user.email, "setup@setup.com")
        with app.app_context():
            form = UserUpdateForm()
            form.username.data = 'updated_username'
            form.email.data = 'updated@updated.com'
            self.user.update(form)
            # if you dont commit here, self.user.username will be a tuple
            db.session.add(self.user)
            db.session.commit()
            # after update
            self.assertEqual(self.user.username, "updated_username")
            self.assertEqual(self.user.email, "updated@updated.com")

    def test_signup_user(self):
        """test User.signup method"""
        with app.app_context():
            user = User.signup(
                email="test@test.com",
                username="testuser",
                password="HASHED_PASSWORD",
                image_url=User.image_url.default.arg,
            )
            db.session.commit()
            # password should now be a hashed password
            self.assertFalse(user.password == 'HASHED_PASSWORD')
            # user is found in the database
            found_user = User.query.get_or_404(user.id)
            self.assertEqual(found_user.id, user.id)

    def test_follow_unfollow_user(self):
        """test connection between User & Follows table"""
        with app.app_context():
            user = User.signup(
                email="test@test.com",
                username="testuser",
                password="HASHED_PASSWORD",
                image_url=User.image_url.default.arg,
            )
            db.session.commit()
            user.following.append(self.user)
            db.session.commit()
            self.assertEqual(len(user.following), 1)
            self.assertEqual(user.following[0].id, self.user.id)
            self.assertEqual(user.following[0].username, self.user.username)

            user.following.remove(self.user)
            db.session.commit()
            self.assertEqual(len(user.following), 0)

    def test_unique_user(self):
        """test that a username or email is not already used by another user"""
        original_user = User.signup(
            email="test@original.com",
            username="original_user",
            password="HASHED_PASSWORD",
            image_url=User.image_url.default.arg,
        )
        db.session.commit()
        copied_user = User.signup(
            email="test@original.com",
            username="new_original_user",
            password="HASHED_PASSWORD",
            image_url=User.image_url.default.arg,
        )
        # email is not unique
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()
        copied_user2 = User.signup(
            email="new_test@original.com",
            username="original_user",
            password="HASHED_PASSWORD",
            image_url=User.image_url.default.arg,
        )
        # username is not unique
        self.assertRaises(IntegrityError, db.session.commit)

    def test_auth_user(self):
        """test authenticate classmethod"""
        user = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=User.image_url.default.arg,
        )
        db.session.commit()

        user_auth = User.authenticate(
            username="testuser",
            password="HASHED_PASSWORD")
        self.assertIsInstance(user_auth, User)

        not_user = User.authenticate(
            username="testuser",
            password='HASHED_PASSWORD123')
        self.assertFalse(not_user)

    def test_user_messages(self):
        """test relation between User Message tables"""
        self.assertEqual(len(self.user.messages), 0)
        msg = Message(text='This is my first message')
        self.user.messages.append(msg)
        db.session.commit()
        # self.assertEqual(len(self.user.messages), 1)
