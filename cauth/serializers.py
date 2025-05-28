from rest_framework.serializers import ModelSerializer
from .models import User, Role, WorkerExtras, HRExtras, Requirements, RequirementTypes, RequirementOptions, Skills, requirement_workers, SkillTags, skills_workers
from .models import Vacancy, vacancy_requirements, vacancy_multiple_options, vacancy_skills
from rest_framework.serializers import PrimaryKeyRelatedField

#----------------------worker-----------------------------
class SkillTagsSerializer(ModelSerializer):
    class Meta:
        model = SkillTags
        fields = ["name"]


class SkillsSerializer(ModelSerializer):
    tags = SkillTagsSerializer(many=True)
    class Meta:
        model = Skills
        fields = ["pk", "name", "tags"]


class SkillsWorkersSerializer(ModelSerializer):
    skill_details = SkillsSerializer(read_only=True, source="skill")
    skill = PrimaryKeyRelatedField(queryset=Skills.objects.all(), write_only=True)
    worker = PrimaryKeyRelatedField(queryset=WorkerExtras.objects.all(), write_only=True)
    class Meta:
        model = skills_workers
        fields = ["pk", "skill", "experience_duration", "experience_level", "description", "skill_details", "worker"]


class RequirementOptionsSerializer(ModelSerializer):
    class Meta:
        model = RequirementOptions
        fields = ["pk", "value"]


class RequirementTypesSerializer(ModelSerializer):
    class Meta:
        model = RequirementTypes
        fields = ["name"]


class RequirementsSerializer(ModelSerializer):
    requirement_type = RequirementTypesSerializer()

    class Meta:
        model = Requirements
        fields = ["pk", "name", "requirement_type", "multiple_answers"]


class RequirementWorkersSerializer(ModelSerializer):
    requirement_details = RequirementsSerializer(read_only=True, source="requirement")
    multiple_options_details = RequirementOptionsSerializer(many=True, read_only=True, source="multiple_options")
    worker = PrimaryKeyRelatedField(queryset=WorkerExtras.objects.all(), write_only=True)
    requirement = PrimaryKeyRelatedField(queryset=Requirements.objects.all(), write_only=True)
    multiple_options = PrimaryKeyRelatedField(queryset=RequirementOptions.objects.all(), many=True, write_only=True, required=False)
    class Meta:
        model = requirement_workers
        fields = ["pk", "requirement", "custom_answer", "multiple_options", "worker", "multiple_options_details", "requirement_details"]


class RoleSerializer(ModelSerializer):
    class Meta:
        model = Role
        fields = ["name"]


class WorkerExtrasSerializer(ModelSerializer):
    get_requirements = RequirementWorkersSerializer(many=True)
    get_skills = SkillsWorkersSerializer(many=True)
    class Meta:
        model = WorkerExtras
        fields = ["get_requirements", "get_skills"]

#-------------------------------vacancy------------------------------
class VacancySkillsSerializer(ModelSerializer):
    skill_details = SkillsSerializer(read_only=True, source="skill")
    vacancy = PrimaryKeyRelatedField(queryset=Vacancy.objects.all(), write_only=True)
    skill = PrimaryKeyRelatedField(queryset=Skills.objects.all(), write_only=True)
    class Meta:
        model = vacancy_skills
        fields = ["pk", "skill", "experience_duration", "experience_level", "description", "vacancy", "skill_details"]


class VacancyRequirementsSerializer(ModelSerializer):
    requirement_details = RequirementsSerializer(read_only=True, source="requirement")
    multiple_options_details = RequirementOptionsSerializer(many=True, source="multiple_options", read_only=True)
    requirement = PrimaryKeyRelatedField(queryset=Requirements.objects.all(), write_only=True)
    multiple_options = PrimaryKeyRelatedField(queryset=RequirementOptions.objects.all(), many=True, write_only=True)
    vacancy = PrimaryKeyRelatedField(queryset=Vacancy.objects.all(), write_only=True)
    class Meta:
        model = vacancy_requirements
        fields = ["pk", "requirement", "custom_answer", "multiple_options", "vacancy", "multiple_options_details", "requirement_details"]

#-----------------------------------hr-----------------------------------
class ShortVacancySerializer(ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ["pk", "title", "visible", "hr"]


class HRExtrasSerializer(ModelSerializer):
    get_vacancies = ShortVacancySerializer(many=True)
    class Meta:
        model = HRExtras
        fields = ["get_vacancies"]

#-------------------Profile--------------------------

class OwnProfileSeriaizer(ModelSerializer):
    roles = RoleSerializer(many=True)
    class Meta:
        model = User
        fields = ["pk", "username", "full_name", "email", "phone", "photo", "description", "roles", "get_related_extras"]


class OtherProfileSeriaizer(ModelSerializer):
    roles = RoleSerializer(many=True)
    class Meta:
        model = User
        fields = ["pk", "username", "full_name", "photo", "description", "roles"]


class FullVacancySerializer(ModelSerializer):  #this zalupina works only below HRExtrasSerializer class definition. Dont ask me why
    get_requirements = VacancyRequirementsSerializer(many=True, read_only=True)
    get_skills = VacancySkillsSerializer(many=True, read_only=True)
    hr = PrimaryKeyRelatedField(queryset=HRExtras.objects.all())
    class Meta:
        model = Vacancy
        fields = ["pk", "title", "description", "hr", "visible", "get_requirements", "get_skills"]


class WhoamiProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "pk"]