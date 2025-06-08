import django_filters
from .models import Vacancy, Requirements, Skills, RequirementOptions, WorkerExtras
class VacanciesFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    requirements = django_filters.ModelMultipleChoiceFilter(field_name="related_vr__requirement", queryset=Requirements.objects.all())
    skills = django_filters.ModelMultipleChoiceFilter(field_name="related_vs__skill", queryset=Skills.objects.all())
    options = django_filters.ModelMultipleChoiceFilter(field_name="related_vr__related_vmo__option", queryset=RequirementOptions.objects.all())
    class Meta:
        model = Vacancy
        fields = ["title", "hr", "requirements", "skills"]
class WorkerExtrasFilter(django_filters.FilterSet):
    requirements = django_filters.ModelMultipleChoiceFilter(field_name="related_rw__requirement", queryset=Requirements.objects.all())
    skills = django_filters.ModelMultipleChoiceFilter(field_name="related_sw__skill", queryset=Skills.objects.all())
    options = django_filters.ModelMultipleChoiceFilter(field_name="related_rw__related_mro__option", queryset=RequirementOptions.objects.all())
    class Meta:
        model = WorkerExtras
        fields = ["requirements", "skills"]