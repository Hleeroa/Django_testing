from rest_framework import serializers, validators
from rest_framework.exceptions import ValidationError

from students.models import Course


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ("id", "name", "students")

    def validate(self, attrs):
        if len(attrs['students']) > 20:
            raise ValidationError('One course should have no more than 20 students')
        return attrs
