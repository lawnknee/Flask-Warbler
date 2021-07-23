"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False



class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        Message.query.delete()
        User.query.delete()

        self.client = app.test_client()

        testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.commit()
        
        self.testuser = User.query.filter_by(username=testuser.username).first()

        # detached instance error: assigning self.testuser before committing to database
        # if we want to use testuser's id, we never get their id until commit() happens
        # if we access self.testuser.id we can potentially run into an error
        

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
            
    
    def test_add_message_logged_out_fail(self):
        """Prevent from adding messages when logged out."""
        
        with self.client as c:
            resp = c.post('/messages/new', data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)
            
            
    def test_delete_message(self):
        """Test deleting a message."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # msg = Message(text="This is a message", user_id=sess[CURR_USER_KEY])
            msg = Message(text="This is a message", user_id=self.testuser.id)

            db.session.add(msg)
            db.session.commit()
            # could have queried for msg id here

            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            m = Message.query.get(msg.id) # purposely getting something that we know is None

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("This is a message", html)
            self.assertIsNone(m) # to confirm that m is None because message no longer exists


    def test_delete_logged_out_fail(self):
        """Prohibits deleting messages when logged out."""
        
        msg = Message(text="This is a message", user_id=self.testuser.id)
        
        db.session.add(msg)
        db.session.commit()
            
        with self.client as c:
            resp = c.get(f"/messages/{msg.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)
            
    def test_show_message(self):
        """Show a specific message."""

        msg = Message(text="This is a message", user_id=self.testuser.id)
        
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            resp = c.get(f"/messages/{msg.id}")
            html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("This is a message", html)

    def test_no_show_nonexistent_message(self):
        """Show 404 error if user tries to access a message that doesn't exist"""

        with self.client as c:
            resp = c.get("/messages/007")

        self.assertEqual(resp.status_code, 404)
      