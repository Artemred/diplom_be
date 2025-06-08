from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Role, users_roles, SavedUsers,
    WorkerExtras, HRExtras, Companies, company_hrs,
    RequirementTypes, Requirements, RequirementOptions,
    requirement_workers, multiple_requirement_options,
    Skills, SkillTags, skills_tags, skills_workers,
    Vacancy, vacancy_skills, vacancy_requirements,
    vacancy_multiple_options, VacancyResponseStatuses,
    VacancyQuickResponses, vacancy_responses, SavedVacancies,
    ComplainReasons, Complains
)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'full_name', 'email', 'phone')
    list_filter = ('is_active', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email', 'phone', 'photo', 'description')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser')}),
    )
    search_fields = ('username', 'full_name', 'email')
    ordering = ('username',)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'extras_content_type')
class UsersRolesAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__full_name')
class SavedUsersAdmin(admin.ModelAdmin):
    list_display = ('owner', 'saved', 'description')
    search_fields = ('owner__username', 'saved__username')
class WorkerExtrasAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__full_name')
class HRExtrasAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__full_name')
class CompaniesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
class CompanyHRsAdmin(admin.ModelAdmin):
    list_display = ('company', 'hr')
    list_filter = ('company',)
    search_fields = ('company__name', 'hr__user__username')
class RequirementTypesAdmin(admin.ModelAdmin):
    list_display = ('name',)
class RequirementsAdmin(admin.ModelAdmin):
    list_display = ('name', 'requirement_type', 'multiple_answers')
    list_filter = ('requirement_type', 'multiple_answers')
    search_fields = ('name',)
class RequirementOptionsAdmin(admin.ModelAdmin):
    list_display = ('requirement', 'value')
    list_filter = ('requirement',)
    search_fields = ('value',)
class RequirementWorkersAdmin(admin.ModelAdmin):
    list_display = ('worker', 'requirement', 'custom_answer')
    list_filter = ('requirement',)
    search_fields = ('worker__user__username', 'requirement__name')
class MultipleRequirementOptionsAdmin(admin.ModelAdmin):
    list_display = ('rw', 'option')
class SkillsAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
class SkillTagsAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
class SkillsTagsAdmin(admin.ModelAdmin):
    list_display = ('skill', 'tag')
    list_filter = ('tag',)
    search_fields = ('skill__name', 'tag__name')
class SkillsWorkersAdmin(admin.ModelAdmin):
    list_display = ('skill', 'worker', 'experience_duration', 'experience_level')
    list_filter = ('experience_level',)
    search_fields = ('skill__name', 'worker__user__username')
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'hr', 'visible')
    list_filter = ('visible',)
    search_fields = ('title', 'hr__user__username')
class VacancySkillsAdmin(admin.ModelAdmin):
    list_display = ('vacancy', 'skill', 'experience_level')
    list_filter = ('experience_level',)
    search_fields = ('vacancy__title', 'skill__name')
class VacancyRequirementsAdmin(admin.ModelAdmin):
    list_display = ('vacancy', 'requirement', 'custom_answer')
    search_fields = ('vacancy__title', 'requirement__name')
class VacancyMultipleOptionsAdmin(admin.ModelAdmin):
    list_display = ('vr', 'option')
class VacancyResponseStatusesAdmin(admin.ModelAdmin):
    list_display = ('name',)
class VacancyQuickResponsesAdmin(admin.ModelAdmin):
    list_display = ('name', 'vacancy', 'related_status')
    list_filter = ('related_status',)
    search_fields = ('name', 'vacancy__title')
class VacancyResponsesAdmin(admin.ModelAdmin):
    list_display = ('worker', 'vacancy', 'creation_date', 'status')
    list_filter = ('status',)
    search_fields = ('worker__user__username', 'vacancy__title')
    date_hierarchy = 'creation_date'
class SavedVacanciesAdmin(admin.ModelAdmin):
    list_display = ('owner', 'vacancy')
    search_fields = ('owner__user__username', 'vacancy__title')
class ComplainReasonsAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority')
    list_filter = ('priority',)
class ComplainsAdmin(admin.ModelAdmin):
    list_display = ('complied', 'complier', 'reason', 'date', 'status')
    list_filter = ('reason', 'status')
    search_fields = ('complied__username', 'complier__username')
    date_hierarchy = 'date'
admin.site.register(User, UserAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(users_roles, UsersRolesAdmin)
admin.site.register(SavedUsers, SavedUsersAdmin)
admin.site.register(WorkerExtras, WorkerExtrasAdmin)
admin.site.register(HRExtras, HRExtrasAdmin)
admin.site.register(Companies, CompaniesAdmin)
admin.site.register(company_hrs, CompanyHRsAdmin)
admin.site.register(RequirementTypes, RequirementTypesAdmin)
admin.site.register(Requirements, RequirementsAdmin)
admin.site.register(RequirementOptions, RequirementOptionsAdmin)
admin.site.register(requirement_workers, RequirementWorkersAdmin)
admin.site.register(multiple_requirement_options, MultipleRequirementOptionsAdmin)
admin.site.register(Skills, SkillsAdmin)
admin.site.register(SkillTags, SkillTagsAdmin)
admin.site.register(skills_tags, SkillsTagsAdmin)
admin.site.register(skills_workers, SkillsWorkersAdmin)
admin.site.register(Vacancy, VacancyAdmin)
admin.site.register(vacancy_skills, VacancySkillsAdmin)
admin.site.register(vacancy_requirements, VacancyRequirementsAdmin)
admin.site.register(vacancy_multiple_options, VacancyMultipleOptionsAdmin)
admin.site.register(VacancyResponseStatuses, VacancyResponseStatusesAdmin)
admin.site.register(VacancyQuickResponses, VacancyQuickResponsesAdmin)
admin.site.register(vacancy_responses, VacancyResponsesAdmin)
admin.site.register(SavedVacancies, SavedVacanciesAdmin)
admin.site.register(ComplainReasons, ComplainReasonsAdmin)
admin.site.register(Complains, ComplainsAdmin)
