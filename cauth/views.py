from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from .models import User, Role, WorkerExtras, HRExtras, Vacancy, requirement_workers, vacancy_requirements, skills_workers, vacancy_skills, Requirements, Skills, RequirementOptions, vacancy_responses, VacancyResponseStatuses, vacancy_responses, SavedVacancies, SavedUsers, Complains, ComplainReasons
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK, HTTP_403_FORBIDDEN
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .serializers import OwnProfileSeriaizer, OtherProfileSeriaizer, WorkerExtrasSerializer, HRExtrasSerializer, FullVacancySerializer, ShortVacancySerializer, RequirementWorkersSerializer, VacancyRequirementsSerializer, SkillsWorkersSerializer, VacancySkillsSerializer, RequirementsSerializer, SkillsSerializer, RequirementOptionsSerializer, FullVacancySerializer, WhoamiProfileSerializer, VacancyResponsesSerializer, SavedVacanciesSerializer, SavedUsersSerializer, SavedVacanciesSerializer, ShortWorkerSerializer, ShortComplainSerializer, ComplainSerializer, ComplainReasonsSerializer
from .filters import VacanciesFilter, WorkerExtrasFilter
from django.db.models import Q
from chat.models import Chat
import uuid
from collections import Counter


class Register(APIView):
    def post(self, request):
        username = request.data.get("username")
        pwd = request.data.get("password")
        required_fields = {"username": username, "password": pwd}
        errors = []
        for k, v in required_fields.items():
            if not v:
                errors.append({k: "this field is required"})
        if errors:
            return Response(errors, status=HTTP_400_BAD_REQUEST)
        
        try:
            User.objects.create_user(username=username, password=pwd)
        except:
            return Response({"username": "user with such username already exists"}, status=HTTP_400_BAD_REQUEST)

        return Response({}, status=HTTP_201_CREATED)


class OccupiedUsernames(APIView):
    def get(self, request, username):  # idempotent, no need to post
        try:
            User.objects.get(username=username)
            return Response({"occupied": True})
        except User.DoesNotExist:
            return Response({"occupied": False})


class ProfileView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=-1):  # get profile info(your or others)
        if pk == -1:
            pk = request.user.pk
        try:
            u = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=HTTP_400_BAD_REQUEST)
        if request.user.pk == pk:  # users own profile
            serializer = OwnProfileSeriaizer(u)
        else:  # other users profile
            serializer = OtherProfileSeriaizer(u)  # TODO preferences for outer profiles
        return Response(serializer.data, status=HTTP_200_OK)

    def patch(self, request, pk=-1):  # update profile info
        if pk == -1:
            pk = request.user.pk
        if pk != request.user.pk:
            return Response({"error": "Authorized user cant change this profile"}, status=HTTP_400_BAD_REQUEST)
        serializer = OwnProfileSeriaizer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=HTTP_200_OK)

    def delete(self, request, pk=-1):  # delete profile
        if pk == -1:
            pk = request.user.pk
        if pk != request.user.pk:
            return Response({"error": "Authorized user cant delete this profile"}, status=HTTP_400_BAD_REQUEST)
        request.user.delete()
        return Response({}, status=HTTP_200_OK)


class ProfileExtrasAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    extras_serializers_mapping = {WorkerExtras: WorkerExtrasSerializer, HRExtras: HRExtrasSerializer}

    def get(self, request, pk, extras):
        try:
            u = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=HTTP_400_BAD_REQUEST)
        try:
            extras_instance = u.get_extras_for_role(extras)
        except Exception as e:
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)
        serializer = self.extras_serializers_mapping[extras_instance.__class__](extras_instance)
        return Response(serializer.data, status=HTTP_200_OK)

    def patch(self, request, pk, extras):
        pass

    
class VacancyAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        try:
            vacancy = Vacancy.objects.get(pk=pk)
        except Vacancy.DoesNotExist:
            return Response({"error": "vacancy does not exists"}, status=HTTP_400_BAD_REQUEST)
        serializer = FullVacancySerializer(vacancy)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            vacancy = Vacancy.objects.get(pk=pk)
        except Vacancy.DoesNotExist:
            return Response({"error": "vacancy does not exists"}, status=HTTP_400_BAD_REQUEST)
        owner = vacancy.hr.get_related_user()
        if owner != request.user:
            return Response({}, status=HTTP_403_FORBIDDEN)
        serializer = FullVacancySerializer(vacancy, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({}, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            vacancy = Vacancy.objects.get(pk=pk)
        except Vacancy.DoesNotExist:
            return Response({"error": "vacancy does not exists"}, status=HTTP_400_BAD_REQUEST)
        owner = vacancy.hr.get_related_user()
        if owner != request.user:
            return Response({}, status=HTTP_403_FORBIDDEN)
        vacancy.delete()
        return Response({}, status=HTTP_200_OK)


class VacancyCreationAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    def post(self, request):
        try:
            extras = request.user.get_extras_for_role("HR")
        except:
            return Response({"error": "not enough permissions"}, status=HTTP_403_FORBIDDEN)
        data = request.data.copy()
        data["hr"] = extras.pk
        serializer = FullVacancySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class VacancyListAPIView(APIView):
    def post(self, request):
        qs = Vacancy.objects.filter(visible=True).select_related("hr").prefetch_related("related_vr").prefetch_related("related_vs")
        filterset = VacanciesFilter(request.data, queryset=qs)
        if filterset.is_valid():
            filtered_queryset = filterset.qs
        else:
            return Response([], status=HTTP_400_BAD_REQUEST)
        serializer = ShortVacancySerializer(filtered_queryset, many=True)
        data = serializer.data
        if request.data.get("worker", None):
            worker = request.user.get_extras_for_role("Worker")
            data = self.calculate_relevance(data, filtered_queryset, worker)
        return Response(data)
    
    def calculate_relevance(self, data, queryset, worker):  # now here are vacancies in qs and worker sep
        worker_skills = worker.related_sw.all()

        for i, j in zip(data, queryset):
            explain = {}
            relevance = 0
            vacancy_skills = j.related_vs.all()
            relevance_count = dict(Counter(vacancy_skills.values_list("relevance", flat=True)))
            relevance_sum = sum(relevance_count.keys())
            wages = {i.skill_id:((100/relevance_sum)*i.relevance)/relevance_count[i.relevance] for i in vacancy_skills}
            for skill in worker_skills:
                if skill.skill_id in wages:
                    relevance += wages[skill.skill_id]
                    explain[skill.skill.name] = wages[skill.skill_id]
            i["relevance"] = relevance
            i["explain"] = explain
        return data


class WorkerListAPIView(APIView):
    def post(self, request):
        qs = WorkerExtras.objects.all().select_related("user").prefetch_related("related_rw").prefetch_related("related_sw", "related_sw__skill")
        filterset = WorkerExtrasFilter(request.data, queryset=qs)
        if filterset.is_valid():
            filtered_queryset = filterset.qs
        else:
            return Response([], status=HTTP_400_BAD_REQUEST)
        serializer = ShortWorkerSerializer(filtered_queryset, many=True)
        if request.data.get("vacancy", None):
            vacancy = Vacancy.objects.prefetch_related("related_vs").get(pk=request.data["vacancy"])
            data = self.calculate_relevance(serializer.data, filtered_queryset, vacancy)
        else:
            data = serializer.data
        return Response(data)

    def calculate_relevance(self, data, queryset, vacancy):
        vacancy_skills = vacancy.related_vs.all()
        relevance_count = dict(Counter(vacancy_skills.values_list("relevance", flat=True)))
        relevance_sum = sum(relevance_count.keys())
        wages = {i.skill_id:((100/relevance_sum)*i.relevance)/relevance_count[i.relevance] for i in vacancy_skills}
        #print(wages)
        for i, j in zip(data, queryset):
            explain = {}
            worker_skills = list(j.related_sw.all())
            relevance = 0
            for skill in worker_skills:
                if skill.skill_id in wages:
                    relevance += wages[skill.skill_id]
                    explain[skill.skill.name] = wages[skill.skill_id]
            i["relevance"] = relevance
            i["explain"] = explain
        return data


class OwnVacanciesAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Vacancy.objects.filter(hr=request.user.get_extras_for_role("HR"))
        serializer = ShortVacancySerializer(qs, many=True)
        return Response(serializer.data)


class WorkerRequirementsAPIVIew(APIView):  # TODO post with similar requirement adds new option
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #Replaceable 
    def get_parent_instance(self, **kwargs):
        return kwargs.get("request").user.get_extras_for_role("Worker")
    
    def get_owner_from_instance(self, instance):
        return instance.__getattribute__(self.insertion_key)
    
    serializer_class=RequirementWorkersSerializer
    model_class = requirement_workers
    insertion_key = "worker"
    role_name = "Worker"


    def post(self, request, pk=-1):
        try:
            extras = self.get_parent_instance(request=request)
        except:
            return Response({"error": "Forbidden"}, status=HTTP_403_FORBIDDEN)
        data = request.data.copy()
        data[self.insertion_key] = extras.pk
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({}, status=HTTP_201_CREATED)
        return Response({"errors": serializer.errors}, status=HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            wr = self.model_class.objects.get(pk=pk)
        except self.model_class.DoesNotExist:
            return Response({"error": "Requirement does not exists"}, status=HTTP_400_BAD_REQUEST)
        try:
            if self.get_owner_from_instance(wr) != request.user.get_extras_for_role(self.role_name):  # TODO
                return Response({"error": "Forbidden"}, status=HTTP_403_FORBIDDEN)
        except:
            return Response({"error": "forbidden"}, status=HTTP_403_FORBIDDEN)
        wr.delete()
        return Response({}, status=HTTP_200_OK)


class VacancyRequirementsAPIView(WorkerRequirementsAPIVIew):
    def get_parent_instance(self, **kwargs):
        return Vacancy.objects.get(pk=kwargs.get("request").data["vacancy"])
    
    def get_owner_from_instance(self, instance):
        return instance.__getattribute__(self.insertion_key).hr

    serializer_class = VacancyRequirementsSerializer
    insertion_key = "vacancy"
    model_class = vacancy_requirements
    role_name = "HR"


class WorkerSkillsAPIView(WorkerRequirementsAPIVIew):
    serializer_class = SkillsWorkersSerializer
    model_class = skills_workers


class VacancySkillsAPIView(VacancyRequirementsAPIView):
    serializer_class = VacancySkillsSerializer
    model_class = vacancy_skills


class RequirementsListAPIView(APIView):  # TODO group or both
    def get(self, request, group, part=""):
        data = Requirements.objects.filter(Q(requirement_type__name=group) | Q(requirement_type__name="Both"))
        if part:
            data = data.filter(name__icontains=part)
        serializer = RequirementsSerializer(data, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class RequirementsOptionsAPIView(APIView):
    def get(self, request, requirement):
        data = RequirementOptions.objects.filter(requirement__pk=requirement)
        serializer = RequirementOptionsSerializer(data, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class SkillsListAPIView(APIView):
    def get(self, request, part=""):
        data = Skills.objects.all()
        if part:
            data = data.filter(name__icontains=part)
        serializer = SkillsSerializer(data, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class WhoamiAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = WhoamiProfileSerializer(request.user)
        return Response(serializer.data, status=HTTP_200_OK)


class AddRoleAPIView(APIView):
    def post(self, request):
        u = request.user
        u.add_role(request.data["role"])
        return Response({}, status=HTTP_200_OK)


class VacancyResponsesAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):  # for vacancy
        try:
            vacancy = Vacancy.objects.prefetch_related("related_responses").get(pk=pk)
        except Vacancy.DoesNotExist:
            return Response({"error": "vacancy does not exists"}, status=HTTP_400_BAD_REQUEST)
        serializer = VacancyResponsesSerializer(vacancy.related_responses, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
    
    def post(self, request, pk):
        try:
            vacancy = Vacancy.objects.select_related("hr", "hr__user").get(pk=pk)
        except Vacancy.DoesNotExist:
            return Response({"error": "vacancy does not exists"}, status=HTTP_400_BAD_REQUEST)
        try:
            worker = request.user.get_extras_for_role("Worker")
        except:
            return Response({"error": "Forbidden"}, status=HTTP_403_FORBIDDEN)
        if vacancy_responses.objects.select_related("vacancy", "worker").filter(vacancy__pk=pk, worker__pk=request.user.get_extras_for_role("Worker").pk).exists():
            return Response({"error": "response already exists"}, status=HTTP_400_BAD_REQUEST)
        else:
            vacancy_responses.objects.create(vacancy=vacancy, worker=worker, status=VacancyResponseStatuses.objects.get(name="Created"))
            if not Chat.objects.filter(user1=request.user, user2=vacancy.hr.user).exists():
                Chat.objects.create(user1=request.user, user2=vacancy.hr.user, title="Vacancy " + vacancy.title, chat_key=str(uuid.uuid4()), vacancy=vacancy)
            return Response({}, status=HTTP_200_OK)
    
    def delete(self, request, pk):
        try:
            response = vacancy_responses.objects.select_related("vacancy", "worker").get(vacancy__pk=pk, worker__pk=request.user.get_extras_for_role("Worker").pk)
        except vacancy_responses.DoesNotExist:
            return Response({"error": "response does not exists"}, status=HTTP_400_BAD_REQUEST)
        response.delete()
        return Response({}, status=HTTP_200_OK)
    
    def patch(self, request, pk):
        try:
            response = vacancy_responses.objects.select_related("vacancy", "worker").get(pk=pk)
        except vacancy_responses.DoesNotExist:
            return Response({"error": "response does not exists"}, status=HTTP_400_BAD_REQUEST)
        response.status = VacancyResponseStatuses.objects.get(name=request.data["status"])
        response.save()
        return Response({}, status=HTTP_200_OK)


class WorkerResponsesAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            worker = request.user.get_extras_for_role("Worker")
        except:
            return Response({"error": "Forbidden"}, status=HTTP_403_FORBIDDEN)
        responses = worker.related_responses.all()
        serializer = VacancyResponsesSerializer(responses, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class SavedVacanciesListAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            worker = request.user.get_extras_for_role("Worker")
        except:
            return Response({"error": "Forbidden"}, status=HTTP_403_FORBIDDEN)
        saved = SavedVacancies.objects.filter(owner=worker)
        serializer = SavedVacanciesSerializer(saved, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def post(self, request):
        try:
            worker = request.user.get_extras_for_role("Worker")
        except:
            return Response({"error": "Forbidden"}, status=HTTP_403_FORBIDDEN)
        try:
            vacancy = Vacancy.objects.get(pk=request.data["vacancy"])
        except Vacancy.DoesNotExist:
            return Response({"error": "vacancy does not exists"}, status=HTTP_400_BAD_REQUEST)
        if SavedVacancies.objects.filter(owner=worker, vacancy=vacancy).exists():
            return Response({"error": "vacancy already saved"}, status=HTTP_400_BAD_REQUEST)
        SavedVacancies.objects.create(owner=worker, vacancy=vacancy)
        return Response({}, status=HTTP_201_CREATED)


class SavedVacanciesDeleteAPIView(APIView):
    def delete(self, request, pk):
        try:
            worker = request.user.get_extras_for_role("Worker")
        except:
            return Response({"error": "Forbidden"}, status=HTTP_403_FORBIDDEN)
        try:
            saved = SavedVacancies.objects.get(pk=pk)
        except SavedVacancies.DoesNotExist:
            return Response({"error": "Saved vacancy does not exists"}, status=HTTP_400_BAD_REQUEST)
        if saved.owner != worker:
            return Response({"error": "Forbidden"}, status=HTTP_403_FORBIDDEN)
        saved.delete()
        return Response({}, status=HTTP_200_OK)


class SavedUsersListAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        saved = SavedUsers.objects.filter(owner=request.user)
        serializer = SavedUsersSerializer(saved, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def post(self, request):
        try:
            user = User.objects.get(pk=request.data["user"])
        except User.DoesNotExist:
            return Response({"error": "User does not exists"}, status=HTTP_400_BAD_REQUEST)
        if SavedUsers.objects.filter(owner=request.user, saved=user).exists():
            return Response({"error": "User already saved"}, status=HTTP_400_BAD_REQUEST)
        SavedUsers.objects.create(owner=request.user, saved=user, description=request.data["description"])
        return Response({}, status=HTTP_201_CREATED)


class SavedUsersDeleteAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            saved = SavedUsers.objects.get(pk=pk)
        except SavedUsers.DoesNotExist:
            return Response({"error": "Saved user does not exists"}, status=HTTP_400_BAD_REQUEST)
        if saved.owner != request.user:
            return Response({"error": "Forbidden"}, status=HTTP_403_FORBIDDEN)
        saved.delete()
        return Response({}, status=HTTP_200_OK)


class CreateChatAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = User.objects.get(pk=request.data["user"])
        except User.DoesNotExist:
            return Response({"error": "User does not exists"}, status=HTTP_400_BAD_REQUEST)
        try:
            vacancy = Vacancy.objects.get(pk=request.data["vacancy"])
        except Vacancy.DoesNotExist:
            return Response({"error": "Vacancy does not exists"}, status=HTTP_400_BAD_REQUEST)
        
        if vacancy_responses.objects.filter(vacancy=vacancy, worker=user.get_extras_for_role("Worker")).exists():
            return Response({"error": "Response already exists", "chat_key": Chat.objects.get(Q(user1=request.user, user2=user) | Q(user1=user, user2=request.user)).chat_key}, status=HTTP_400_BAD_REQUEST)
        else:
            vacancy_responses.objects.create(vacancy=vacancy, worker=user.get_extras_for_role("Worker"), status=VacancyResponseStatuses.objects.get(name="Created"))
            if not Chat.objects.filter(user1=request.user, user2=user).exists():
                chat = Chat.objects.create(user1=request.user, user2=user, title="Vacancy " + vacancy.title, chat_key=str(uuid.uuid4()), vacancy=vacancy)
                return Response({"chat_key": chat.chat_key}, status=HTTP_201_CREATED)
            else:
                return Response({"chat_key": Chat.objects.filter(user1=request.user, user2=user).first().chat_key}, status=HTTP_201_CREATED)


class ComplainReasonsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reasons = ComplainReasons.objects.all().order_by('priority')
        serializer = ComplainReasonsSerializer(reasons, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class ComplainAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if "Moderator" in request.user.roles.values_list("name", flat=True):
            complains = Complains.objects.all()
            serializer = ShortComplainSerializer(complains, many=True)
            return Response(serializer.data, status=HTTP_200_OK)
        else:
            return Response({"error": "Forbidden"}, status=HTTP_403_FORBIDDEN)

    def post(self, request):
        try:
            if request.data["target_type"] == "Profile":
                user = User.objects.get(pk=request.data["target_pk"])
            elif request.data["target_type"] == "Vacancy":
                user = Vacancy.objects.get(pk=request.data["target_pk"]).hr.get_related_user()
        except User.DoesNotExist:
            return Response({"error": "User does not exists"}, status=HTTP_400_BAD_REQUEST)
        try:
            reason = ComplainReasons.objects.get(pk=request.data["reason"])
        except ComplainReasons.DoesNotExist:
            return Response({"error": "Reason does not exists"}, status=HTTP_400_BAD_REQUEST)
        Complains.objects.create(complier=request.user, complied=user, reason=reason, description=request.data["description"], target_type=request.data["target_type"], target_pk=request.data["target_pk"])
        return Response({}, status=HTTP_201_CREATED)


class ComplainDetailsAPIView(APIView):
    def get(self, request, pk):
        if "Moderator" not in request.user.roles.values_list("name", flat=True):
            return Response({"error": "Forbidden"}, status=HTTP_403_FORBIDDEN)
        try:
            complain = Complains.objects.get(pk=pk)
        except Complains.DoesNotExist:
            return Response({"error": "Complain does not exists"}, status=HTTP_400_BAD_REQUEST)
        serializer = ComplainSerializer(complain)
        return Response(serializer.data, status=HTTP_200_OK)
    
    def delete(self, request, pk):
        if "Moderator" not in request.user.roles.values_list("name", flat=True):
            return Response({"error": "Forbidden"}, status=HTTP_403_FORBIDDEN)
        try:
            complain = Complains.objects.get(pk=pk)
        except Complains.DoesNotExist:
            return Response({"error": "Complain does not exists"}, status=HTTP_400_BAD_REQUEST)
        complain.delete()
        return Response({}, status=HTTP_200_OK)
    
    def patch(self, request, pk):
        if "Moderator" not in request.user.roles.values_list("name", flat=True):
            return Response({"error": "Forbidden"}, status=HTTP_403_FORBIDDEN)
        try:
            complain = Complains.objects.get(pk=pk)
        except Complains.DoesNotExist:
            return Response({"error": "Complain does not exists"}, status=HTTP_400_BAD_REQUEST)
        serializer = ComplainSerializer(complain, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    