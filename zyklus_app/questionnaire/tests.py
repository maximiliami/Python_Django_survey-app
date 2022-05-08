from django.test import TestCase
from django.contrib.auth import get_user_model
from questionnaire.models import Pair


# Create your tests here.
class UserAccountTests(TestCase):

    def test_new_superuser(self):
        db = get_user_model()
        super_user = db.objects.create_superuser('maxim', 'password')
        self.assertEquals(super_user.user_code, 'maxim')
        self.assertEquals(super_user.is_superuser, True)
        self.assertEquals(super_user.is_active, True)
        self.assertEquals(super_user.is_staff, True)

        with self.assertRaises(ValueError):
            db.objects.create_superuser(user_code='Max', password='password', is_superuser=False)

        with self.assertRaises(ValueError):
            db.objects.create_superuser(user_code='Max', password='password', is_staff=False)

    def test_new_pseudouser(self):
        db = get_user_model()
        user = db.objects.create_user('maxim', 'password')
        self.assertEquals(user.user_code, 'maxim')
        self.assertEquals(user.is_superuser, False)
        self.assertEquals(user.is_staff, False)


class PairTests(TestCase):

    def test_new_pair(self):
        pair = Pair("Frankenstein")
        pair.ident = "Frankenstein"
        self.assertEquals(pair.ident, "Frankenstein")
        self.assertEquals(str(pair), "Frankenstein")
