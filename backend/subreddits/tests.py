from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Rule, Subreddit

User = get_user_model()


class SubredditViewSetTests(APITestCase):
    def setUp(self):
        # NOTE: Ensure every user has a unique email.
        self.user_one = User.objects.create_user(
            username="userone", password="password123", email="userone@example.com"
        )
        self.user_two = User.objects.create_user(
            username="usertwo", password="password123", email="usertwo@example.com"
        )
        self.subreddit = Subreddit.objects.create(
            name="test_subreddit", owner=self.user_one, description="A test."
        )
        self.subreddit.moderators.add(self.user_one)

    def test_list_subreddits_unauthenticated(self):
        url = reverse("subreddit-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # FIX: The response data is a list, not a dictionary with a 'results' key.
        self.assertEqual(len(response.data), 1)

    def test_create_subreddit_authenticated(self):
        # FIX: Use force_authenticate for DRF's test client, not login().
        self.client.force_authenticate(user=self.user_two)
        url = reverse("subreddit-list")
        data = {"name": "new_community", "description": "A brand new place."}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subreddit.objects.count(), 2)
        new_subreddit = Subreddit.objects.get(name="new_community")
        self.assertEqual(new_subreddit.owner, self.user_two)
        self.assertTrue(new_subreddit.moderators.filter(pk=self.user_two.pk).exists())

    def test_create_subreddit_unauthenticated(self):
        url = reverse("subreddit-list")
        data = {"name": "another_community"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_subreddit_by_owner(self):
        # FIX: Use force_authenticate.
        self.client.force_authenticate(user=self.user_one)
        url = reverse("subreddit-detail", kwargs={"pk": self.subreddit.pk})
        data = {"description": "An updated description."}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.subreddit.refresh_from_db()
        self.assertEqual(self.subreddit.description, "An updated description.")

    def test_update_subreddit_by_non_owner(self):
        # FIX: Use force_authenticate.
        self.client.force_authenticate(user=self.user_two)
        url = reverse("subreddit-detail", kwargs={"pk": self.subreddit.pk})
        data = {"description": "Trying to hack."}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_subreddit_by_owner(self):
        # FIX: Use force_authenticate.
        self.client.force_authenticate(user=self.user_one)
        url = reverse("subreddit-detail", kwargs={"pk": self.subreddit.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subreddit.objects.filter(pk=self.subreddit.pk).exists())


class ModeratorViewSetTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", password="password123", email="owner@example.com"
        )
        self.mod_to_be = User.objects.create_user(
            username="modtobe", password="password123", email="modtobe@example.com"
        )
        self.regular_user = User.objects.create_user(
            username="regular", password="password123", email="regular@example.com"
        )
        self.subreddit = Subreddit.objects.create(name="modtest", owner=self.owner)
        self.subreddit.moderators.add(self.owner)

    def test_owner_can_add_moderator(self):
        # FIX: Use force_authenticate.
        self.client.force_authenticate(user=self.owner)
        url = reverse(
            "subreddit-moderators-list", kwargs={"subreddit_pk": self.subreddit.pk}
        )
        data = {"id": self.mod_to_be.pk}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.subreddit.moderators.filter(pk=self.mod_to_be.pk).exists())

    def test_non_owner_cannot_add_moderator(self):
        # FIX: Use force_authenticate.
        self.client.force_authenticate(user=self.regular_user)
        url = reverse(
            "subreddit-moderators-list", kwargs={"subreddit_pk": self.subreddit.pk}
        )
        data = {"id": self.mod_to_be.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_existing_moderator_fails(self):
        # FIX: Use force_authenticate.
        self.client.force_authenticate(user=self.owner)
        url = reverse(
            "subreddit-moderators-list", kwargs={"subreddit_pk": self.subreddit.pk}
        )
        data = {"id": self.owner.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_can_remove_moderator(self):
        self.subreddit.moderators.add(self.mod_to_be)
        # FIX: Use force_authenticate.
        self.client.force_authenticate(user=self.owner)
        url = reverse(
            "subreddit-moderators-detail",
            kwargs={"subreddit_pk": self.subreddit.pk, "pk": self.mod_to_be.pk},
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            self.subreddit.moderators.filter(pk=self.mod_to_be.pk).exists()
        )

    def test_owner_cannot_remove_themselves(self):
        # FIX: Use force_authenticate.
        self.client.force_authenticate(user=self.owner)
        url = reverse(
            "subreddit-moderators-detail",
            kwargs={"subreddit_pk": self.subreddit.pk, "pk": self.owner.pk},
        )
        response = self.client.delete(url)
        # This now correctly tests the logic inside the view, not an auth failure.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(self.subreddit.moderators.filter(pk=self.owner.pk).exists())


class RuleViewSetTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner-rules",
            password="password123",
            email="owner-rules@example.com",
        )
        self.moderator = User.objects.create_user(
            username="moderator-rules",
            password="password123",
            email="moderator-rules@example.com",
        )
        self.regular_user = User.objects.create_user(
            username="regular-rules",
            password="password123",
            email="regular-rules@example.com",
        )
        self.subreddit = Subreddit.objects.create(name="ruletest", owner=self.owner)
        self.subreddit.moderators.add(self.owner, self.moderator)
        self.rule = Rule.objects.create(
            subreddit=self.subreddit, title="Rule 1", description="No spam."
        )

    def test_any_user_can_list_rules(self):
        url = reverse(
            "subreddit-rules-list", kwargs={"subreddit_pk": self.subreddit.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # FIX: The response data is a list.
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Rule 1")

    def test_moderator_can_create_rule(self):
        self.client.force_authenticate(user=self.moderator)
        url = reverse(
            "subreddit-rules-list", kwargs={"subreddit_pk": self.subreddit.pk}
        )
        data = {"title": "Rule 2", "description": "Be excellent to each other."}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.subreddit.rules.count(), 2)

    def test_regular_user_cannot_create_rule(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse(
            "subreddit-rules-list", kwargs={"subreddit_pk": self.subreddit.pk}
        )
        data = {"title": "Bad Rule", "description": "I am not a mod."}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_can_delete_rule(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse(
            "subreddit-rules-detail",
            kwargs={"subreddit_pk": self.subreddit.pk, "pk": self.rule.pk},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.subreddit.rules.count(), 0)
