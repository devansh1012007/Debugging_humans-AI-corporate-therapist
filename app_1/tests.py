from django.test import TestCase
from .models import OrgNode
from .tasks import generate_drill_down_lists
users = OrgNode.objects.all()
for user in users:
    generate_drill_down_lists(user)