from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from .models import User, Role, WorkerExtras, HRExtras, Vacancy, requirement_workers, vacancy_requirements, skills_workers, vacancy_skills, Requirements, Skills, RequirementOptions
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK, HTTP_403_FORBIDDEN
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .serializers import OwnProfileSeriaizer, OtherProfileSeriaizer, WorkerExtrasSerializer, HRExtrasSerializer, FullVacancySerializer, ShortVacancySerializer, RequirementWorkersSerializer, VacancyRequirementsSerializer, SkillsWorkersSerializer, VacancySkillsSerializer, RequirementsSerializer, SkillsSerializer, RequirementOptionsSerializer, FullVacancySerializer, WhoamiProfileSerializer
from .filters import VacanciesFilter
from django.db.models import Q


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
        return Response(serializer.data)


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
    