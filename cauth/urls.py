from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import Register, OccupiedUsernames, ProfileView, ProfileExtrasAPIView, VacancyAPIView, WorkerRequirementsAPIVIew, VacancyRequirementsAPIView, WorkerSkillsAPIView, VacancySkillsAPIView, RequirementsListAPIView, SkillsListAPIView, RequirementsOptionsAPIView, VacancyListAPIView, VacancyCreationAPIView, WhoamiAPIView, OwnVacanciesAPIView, AddRoleAPIView, WorkerResponsesAPIView, VacancyResponsesAPIView, SavedUsersListAPIView, SavedUsersDeleteAPIView, SavedVacanciesListAPIView, SavedVacanciesDeleteAPIView

app_name = "cauth"

urlpatterns = [
    path("auth/", obtain_auth_token),
    path("auth/register/", Register.as_view()),
    path("auth/occupied/<str:username>", OccupiedUsernames.as_view()),
    path("profile/<int:pk>", ProfileView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("profile/extras/<int:pk>/<str:extras>", ProfileExtrasAPIView.as_view()),
    path("profile/whoami", WhoamiAPIView.as_view()),
    path("profile/add-role/", AddRoleAPIView.as_view()),  # post
    path("profile/responses/", WorkerResponsesAPIView.as_view()),  # get from profile
    path("profile/saved-users/", SavedUsersListAPIView.as_view()),  # get post
    path("profile/saved-users/<int:pk>", SavedUsersDeleteAPIView.as_view()),  # delete

    path("vacancies/<int:pk>", VacancyAPIView.as_view()),  # get(retrieve) patch delete
    path("vacancies/", VacancyCreationAPIView.as_view()),  # post
    path("vacancies/list/", VacancyListAPIView.as_view()),  # post(list) [too much filtering parameters]
    path("vacancies/own/", OwnVacanciesAPIView.as_view()),  # get
    path("vacancies/responses/<int:pk>", VacancyResponsesAPIView.as_view()),  # get post from vacancy
    path("vacancies/saved-vacancies/", SavedVacanciesListAPIView.as_view()),  # get post
    path("vacancies/saved-vacancies/<int:pk>", SavedVacanciesDeleteAPIView.as_view()),  # delete

    path("requirements/worker/<int:pk>", WorkerRequirementsAPIVIew.as_view()),  # delete
    path("requirements/worker/", WorkerRequirementsAPIVIew.as_view()),  # post
    path("requirements/vacancy/<int:pk>", VacancyRequirementsAPIView.as_view()),  # delete
    path("requirements/vacancy/", VacancyRequirementsAPIView.as_view()),  # post
    path("skills/worker/<int:pk>", WorkerSkillsAPIView.as_view()),  # delete
    path("skills/worker/", WorkerSkillsAPIView.as_view()),  # post
    path("skills/vacancy/<int:pk>", VacancySkillsAPIView.as_view()),  # delete
    path("skills/vacancy/", VacancySkillsAPIView.as_view()),  # post
    path("requirements/list/<str:group>/<str:part>", RequirementsListAPIView.as_view()),
    path("requirements/list/<str:group>/", RequirementsListAPIView.as_view()),  # no filtering
    path("requirements/options/<str:requirement>", RequirementsOptionsAPIView.as_view()),
    path("skills/list/<str:part>", SkillsListAPIView.as_view()),  # with filtr
    path("skills/list/", SkillsListAPIView.as_view())  # no filtering
]