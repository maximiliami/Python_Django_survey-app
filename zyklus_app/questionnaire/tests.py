from django.test import TestCase
from django.contrib.auth import get_user_model


# Create your tests here.
class UserAccountTests(TestCase):

    def test_new_superuser(self):
        db = get_user_model()
        super_user = db.objects.create_superuser('maxim', 'password')
        self.assertEquals(super_user.user_code, 'maxim')
        self.assertEquals(super_user.is_superuser, True)
        self.assertEquals(super_user.is_active, True)
        self.assertEquals(super_user.is_staff, True)
