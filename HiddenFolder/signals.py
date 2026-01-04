from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added, social_account_updated

@receiver(social_account_added)
def populate_user_from_social(sender, request, sociallogin, **kwargs):
    """Populate basic User fields from social account data when a social account is first added."""
    user = sociallogin.user
    data = sociallogin.account.extra_data or {}

    # Common fields across providers
    name = data.get('name') or data.get('login') or ''
    given_name = data.get('given_name') or data.get('first_name')
    email = data.get('email')

    if not user.first_name and given_name:
        user.first_name = given_name
    elif not user.first_name and name:
        # fallback to full name
        user.first_name = name.split(' ')[0]

    if email and (not user.email):
        user.email = email

    user.save()

@receiver(social_account_updated)
def update_user_from_social(sender, request, sociallogin, **kwargs):
    """Update User fields when social account data is updated."""
    populate_user_from_social(sender, request, sociallogin, **kwargs)