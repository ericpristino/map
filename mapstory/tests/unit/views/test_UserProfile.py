from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from mapstory.tests.AdminClient import AdminClient
from mapstory.tests.MapStoryTestMixin import MapStoryTestMixin

User = get_user_model()

def getTestUser():
    """
    Returns an existing user or
    a new one if no users exist.

    Returns:
        TYPE: User 
    """
    allUsers = User.objects.all()
    if len(allUsers) > 0 :
        return allUsers[0]
    else :
        return User.objects.create_user(username='profiletester',
                                 email='profiletester@mapstorytests.com',
                                 password='superduperpassword2000')

class ProfileDetailViewTest(MapStoryTestMixin):
    def setUp(self):
        self.test_username, self.test_password = self.create_user('testingProfiles', 'testingProfiles')
        self.userclient = AdminClient()

    def tearDown(self):
        pass
    def test_profile_detail_not_found(self):
        # Should build detail URL correctly
        self.assertEqual(reverse('profile_detail', kwargs={'slug': 'nonexistent'}), u'/storyteller/nonexistent/')
        # Should not find this user
        response = self.client.get(reverse('profile_detail', kwargs={'slug': 'nonexistent'}))
        self.assertEqual(response.status_code, 404)

    def test_page_detail_page_response(self):
        # We need an existing user for this
        testUser = getTestUser()
        response = self.client.get(testUser.get_absolute_url())

        # The profile page should exist
        self.assertEqual(response.status_code, 200)

        # Should be using the correct template
        self.assertTemplateUsed(response, 'people/profile_detail.html')
        self.assertContains(response, testUser.first_name)

    def test_get_username_none(self):
        response = self.client.get(reverse('edit_profile', kwargs={'username': None}), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_profile_edit_page_responses(self):
        otherUser = getTestUser()
        other_url = reverse('edit_profile', kwargs={'username':otherUser.username}) 
        self.assertEqual(other_url, 
            u'/storyteller/edit/%s/' % otherUser.username
        )

        # Anonymous users should be redirected to login form
        response = self.client.get(other_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Log in to an existing account')

        # Login with a user
        edit_user_url = reverse('edit_profile', kwargs={'username':self.test_username})
        self.userclient.login_as_non_admin(username=self.test_username, password=self.test_password)
        response = self.userclient.get(edit_user_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_username)
        self.assertTemplateUsed(response, 'people/profile_edit.html')
        self.assertContains(response, 'Edit Your Profile')

        # Create new organization
        form_data = {
            'first_name': 'editedtestname',
            'last_name': 'editedtestname',
        }
        response = self.userclient.post(edit_user_url, data=form_data, follow=True)

        # Should not let other users edit profiles they don't own
        response = self.userclient.get(other_url)
        self.assertEqual(response.status_code, 403)

    def test_profile_delete_anonymous_user_delete(self):
        # Should redirect to the login page
        response = self.client.get(reverse('profile_delete', kwargs={'username':'nonexistentuser'}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

    def test_profile_delete_not_found(self):
        self.userclient.login_as_non_admin(username=self.test_username, password=self.test_password)
        response = self.userclient.get(reverse('profile_delete', kwargs={'username':'nonexistentuser'}), follow=True)
        self.assertEqual(response.status_code, 404)

    def test_profile_delete(self):
        self.userclient.login_as_non_admin(username=self.test_username, password=self.test_password)
        response = self.userclient.get(reverse('profile_delete', kwargs={'username':self.test_username}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'people/profile_delete.html')








