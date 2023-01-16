"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase
from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """test general user views routes in app"""
    def setUp(self):
        """User testcase set up"""
        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_get_users(self):
        """test get users from search"""
        user2 = User.signup(username="testuser2",
                                    email="test2@test2.com",
                                    password="testuser2",
                                    image_url=None)

        db.session.commit()
        # next make a request as user2 searching for original test user
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = user2.id
            
            resp = c.get('/users', data = {'q': self.testuser.username})
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.testuser.username, html)

    def test_get_profile(self):
        """Should get user profile by ID"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(f"/users/{self.testuser.id}")
            html = resp.get_data(as_text=True)
            self.assertIn(f"@{self.testuser.username}", html)
            self.assertIn(f'href="/users/{self.testuser.id}"', html)
            self.assertIn(f'href="/users/{self.testuser.id}/following"', html)
            self.assertIn(f'href="/users/{self.testuser.id}/followers"', html)
            self.assertIn(f'href="/users/{self.testuser.id}/likes"', html)

    
