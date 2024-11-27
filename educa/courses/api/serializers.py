from django.db.models import Count
from rest_framework import serializers
from courses.models import Content, Course, Module, Subject
from students.models import Portfolio, PortContent


class SubjectSerializer(serializers.ModelSerializer):
    total_courses = serializers.IntegerField()
    popular_courses = serializers.SerializerMethodField()

    def get_popular_courses(self, obj):
        courses = obj.courses.annotate(
            total_students=Count('students')
        ).order_by('total_students')[:3]
        return [
            f'{c.title} ({c.total_students})' for c in courses
        ]

    class Meta:
        model = Subject
        fields = ['id', 'title', 'slug', 'total_courses', 'popular_courses']


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['order', 'title', 'description']


# class CourseSerializer(serializers.ModelSerializer):
#     # modules = serializers.StringRelatedField(many=True, read_only=True)
#     modules = ModuleSerializer(many=True, read_only=True)
#     stud_modules = PortfolioSerializer(many=True, read_only=True)

#     class Meta:
#         model = Course
#         fields = [
#             'id',
#             'subject',
#             'title',
#             'slug',
#             'overview',
#             'created',
#             'owner',
#             'modules',
#             'stud_modules'
#             ]


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ['title', 'slug', 'overview']


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    stud_modules = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'subject',
            'title',
            'slug',
            'overview',
            'created',
            'owner',
            'modules',
            'stud_modules'
        ]

    def get_stud_modules(self, obj):

        user = self.context['request'].user

        portfolios = obj.stud_modules.filter(student=user)

        return PortfolioSerializer(portfolios, many=True).data


class ItemRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return value.render()


class ContentSerializer(serializers.ModelSerializer):
    item = ItemRelatedField(read_only=True)

    class Meta:
        model = Content
        fields = ['order', 'item']

class PortContentSerializer(serializers.ModelSerializer):
    item = ItemRelatedField(read_only=True)

    class Meta:
        model = PortContent
        fields = ['order', 'item']

# ....................Module Content................................
class ModuleWithContentsSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True)

    class Meta:
        model = Module
        fields = ['order', 'title', 'description', 'contents']


class PortfolioWithContentsSerializer(serializers.ModelSerializer):
    contents = PortContentSerializer(many=True)

    class Meta:
        model = Portfolio
        fields = ['order', 'title', 'overview', 'contents']


class CourseWithContentsSerializer(serializers.ModelSerializer):
    modules = ModuleWithContentsSerializer(many=True)
    stud_modules = PortfolioWithContentsSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'subject',
            'title',
            'slug',
            'overview',
            'created',
            'owner',
            'modules',
            'stud_modules'
        ]