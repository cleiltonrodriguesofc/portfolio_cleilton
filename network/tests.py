from django.test import TestCase, Client
from .models import User, Post

class NetworkTestCase(TestCase):
    def setUp(self):
        # Create users
        self.u1 = User.objects.create_user("user1", "user1@example.com", "password")
        self.u2 = User.objects.create_user("user2", "user2@example.com", "password")
        self.u3 = User.objects.create_user("user3", "user3@example.com", "password")

        # Create posts
        self.p1 = Post.objects.create(user=self.u1, content="Post 1 content")
        self.p2 = Post.objects.create(user=self.u2, content="Post 2 content")
        
    def test_post_creation(self):
        self.assertEqual(Post.objects.count(), 2)
        
    def test_follow(self):
        self.u1.following.add(self.u2)
        self.assertEqual(self.u1.following.count(), 1)
        self.assertEqual(self.u2.followers.count(), 1)
        self.assertTrue(self.u1.following.filter(pk=self.u2.id).exists())
        
    def test_like(self):
        self.p1.likes.add(self.u2)
        self.assertEqual(self.p1.likes.count(), 1)
        self.assertTrue(self.u2 in self.p1.likes.all())
        
    def test_index_view(self):
        c = Client()
        response = c.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Post 1 content")
        self.assertContains(response, "Post 2 content")
        
    def test_following_view_access(self):
        c = Client()
        # Guest should be redirected
        response = c.get("/following")
        self.assertEqual(response.status_code, 302)
        
        # Logged in
        c.login(username="user1", password="password")
        response = c.get("/following")
        self.assertEqual(response.status_code, 200)
        
    def test_following_content(self):
        c = Client()
        c.login(username="user1", password="password")
        
        # User 1 follows User 2
        self.u1.following.add(self.u2)
        
        response = c.get("/following")
        self.assertContains(response, "Post 2 content")
        
        # User 1 does not follow User 3 (who has no posts yet, let's create one)
        Post.objects.create(user=self.u3, content="Post 3 content")
        
        response = c.get("/following")
        self.assertNotContains(response, "Post 3 content")
        
    def test_edit_permission(self):
        c = Client()
        c.login(username="user1", password="password")
        
        # Try to edit own post
        response = c.put(f"/edit/{self.p1.id}", data='{"content": "Edited Content"}', content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.content, "Edited Content")
        
        # Try to edit other's post
        response = c.put(f"/edit/{self.p2.id}", data='{"content": "Hacked Content"}', content_type="application/json")
        self.assertEqual(response.status_code, 403)
        self.p2.refresh_from_db()
        self.assertEqual(self.p2.content, "Post 2 content")
        
    def test_like_toggle(self):
        c = Client()
        c.login(username="user1", password="password")
        
        # Like
        response = c.put(f"/like/{self.p2.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.p2.likes.count(), 1)
        
        # Unlike
        response = c.put(f"/like/{self.p2.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.p2.likes.count(), 0)
