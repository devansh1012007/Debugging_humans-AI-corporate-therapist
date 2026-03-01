from rest_framework import serializers
from .models import OrgNode, MentalHealthMetric, ReportSnapshot, personalData

class MentalHealthMetricSerializer(serializers.ModelSerializer):
    """Used for POST requests (Users submitting their daily score).
    """
    class Meta:
        model = MentalHealthMetric
        fields = ['wellness_index', 'stress_level', 'note', 'date_recorded']

class OrgNodeSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='structure_level.name', read_only=True)
    class Meta:
        model = OrgNode
        fields = ['id', 'name', 'role', 'parent', 'company']

class ReportSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSnapshot
        fields = ['id', 'report_type', 'created_at', 'data']

class PersonalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = personalData
        fields = ['id', 'owner', 'content']