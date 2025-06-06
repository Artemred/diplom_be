from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.contrib.contenttypes.models import ContentType
from typing import Union, List, Tuple

def fill_db():
    for i in [Role, RequirementTypes, Requirements, RequirementOptions, ComplainReasons, SkillTags, Skills, VacancyResponseStatuses]:
        i.objects.generate()

class UserManager(BaseUserManager):

    def create_user(self, **kwargs):
        u = self.model(username = kwargs["username"])
        u.set_password(kwargs["password"])
        u.save(using=self._db)
        return u

    def create_superuser(self, **kwargs):
        u = self.model(username = kwargs["username"], is_superuser=True, is_staff=True, is_active=True)
        u.set_password(kwargs["password"])
        u.save(using=self._db)
        return u


class RoleManager(models.Manager):
    def generate(self):
        self.create(name="HR", extras_content_type=ContentType.objects.get_for_model(HRExtras))
        self.create(name="Worker", extras_content_type=ContentType.objects.get_for_model(WorkerExtras))
        self.create(name="Moderator")


class RequirementTypesManager(models.Manager):
    def generate(self):
        self.create(name="Worker")
        self.create(name="Vacancy")
        self.create(name="Both")


class RequirementsManager(models.Manager):
    def generate(self):
        worker_type = RequirementTypes.objects.get(name="Worker")
        vacancy_type = RequirementTypes.objects.get(name="Vacancy")
        both_type = RequirementTypes.objects.get(name="Both")
        self.create(name="Working day", requirement_type=both_type, multiple_answers=True)
        self.create(name="Salary", requirement_type=both_type, multiple_answers=True)
        self.create(name="Education", requirement_type=both_type, multiple_answers=False)
        self.create(name="City", requirement_type=both_type, multiple_answers=False)
        self.create(name="Work format", requirement_type=both_type, multiple_answers=True) 


class RequirementOptionsManager(models.Manager):
    def generate(self):
        r = Requirements.objects.get(name="Working day")
        for i in ["8h", "6h", "4h"]:
            self.create(requirement=r, value=i)

        sl = Requirements.objects.get(name="Salary")
        self.create(requirement=sl, value="10000₴-15000₴")
        self.create(requirement=sl, value="15000₴-20000₴")
        self.create(requirement=sl, value="20000₴-25000₴")
        self.create(requirement=sl, value="25000₴-30000₴")
        self.create(requirement=sl, value="30000₴+")
        self.create(requirement=sl, value="50000₴+")
        

        r = Requirements.objects.get(name="Education")
        for i in ["Courses", "Bachelor", "Master", "PhD"]:
            self.create(requirement=r, value=i)
        
        r = Requirements.objects.get(name="City")
        for i in ["Kyiv", "Lviv", "Sumy", "Kharkiv", "Dnipro", "Chernihiv", "Chernobyl", "Zaporizhzhia", "Ivano-Frankivsk", "Mykolaiv", "Odesa", "Poltava", "Simferopol", "Ternopil", "Vinnytsia", "Zhytomyr"]:
            self.create(requirement=r, value=i)
        
        r = Requirements.objects.get(name="Work format")
        for i in ["Local", "Remote"]:
            self.create(requirement=r, value=i)


class ComplainReasonsManager(models.Manager):
    def generate(self):
        self.create(name="Insult", priority=1)


class SkillsManager(models.Manager):
    def generate(self):
        o = self.create(name="Django")
        o.add_tags(["Python", "Backend"])
        o = self.create(name="React")
        o.add_tags(["Frontend", "NodeJS"])
        o = self.create(name="Angular")
        o.add_tags(["Frontend", "NodeJS"])
        o = self.create(name="Vue")
        o.add_tags(["Frontend", "NodeJS"])
        o = self.create(name="Python")
        o.add_tags(["Python"])
        o = self.create(name="Selenium")
        o.add_tags(["Python"])
        o = self.create(name="Docker")
        o.add_tags(["Docker"])
        o = self.create(name="Git")
        o.add_tags(["Git"])
        o = self.create(name="GitHub")
        o.add_tags(["Git"])
        o = self.create(name="GitLab")
        o.add_tags(["Git"])
        o = self.create(name="Bitbucket")
        o.add_tags(["Git"])
        o = self.create(name="Jira")
        o.add_tags(["Project management"])
        o = self.create(name="Trello")
        o.add_tags(["Project management"])
        o = self.create(name="PostgreSQL")
        o.add_tags(["Database"])
        o = self.create(name="MySQL")
        o.add_tags(["Database"])
        o = self.create(name="MongoDB")
        o.add_tags(["Database"])
        o = self.create(name="Redis")
        o.add_tags(["Database"])
        o = self.create(name="Firebase")
        o.add_tags(["Database"])
        o = self.create(name="Firebase")
        o.add_tags(["Database"])
        o = self.create(name="Firebase")
        o.add_tags(["Database"])


class SkillTagsManager(models.Manager):
    def generate(self):
        self.create(name="Backend")
        self.create(name="Frontend")
        self.create(name="Project management")
        self.create(name="C#")
        self.create(name="Python")
        self.create(name="NodeJS")
        self.create(name="Java")
        self.create(name="C++")
        self.create(name="C")
        self.create(name="Go")
        self.create(name="Rust")
        self.create(name="PHP")
        self.create(name="Ruby")
        self.create(name="TypeScript")
        self.create(name="HTML")
        self.create(name="CSS")
        self.create(name="JavaScript")
        self.create(name="Database")
        self.create(name="Docker")
        self.create(name="Git")
        self.create(name="GitHub")
        self.create(name="GitLab")
        self.create(name="Bitbucket")
        self.create(name="Jira")
        self.create(name="Trello")


class VacancyResponseStatusManager(models.Manager):
    def generate(self):
        self.create(name="Created")
        self.create(name="Pending")
        self.create(name="Accepted")
        self.create(name="Rejected")

# --------------------------------profile-----------------------------

class User(AbstractUser):
    first_name = None
    last_name = None
    is_staff = models.BooleanField(default=False)
    date_joined = None
    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    full_name = models.CharField(max_length=64, null=True, blank=True)  # todo null
    email = models.EmailField(max_length=254, null=True, blank=True)
    phone = models.CharField(max_length=12, null=True, blank=True)
    photo = models.ImageField(upload_to="media/photos", null=True, blank=True)
    description = models.CharField(max_length=2048, null=True, blank=True)
    roles = models.ManyToManyField(to="Role", through="users_roles", through_fields=("user", "role"))

    def add_role(self, name: str):
        primary_role = Role.objects.get(name=name)
        users_roles.objects.create(user=self, role=primary_role)
        if primary_role.extras_content_type:
            return primary_role.extras_content_type.model_class().objects.create(user=self)
        return None

    
    def __get_mw_for_role(self, role: Union[str, "Role"]):
        if type(role) is str:
            role = Role.objects.get(name=role)
        elif type(role) is Role:
            pass
        else:
            raise ValueError("Bad input")
        return users_roles.objects.get(user=self, role=role)

    def get_extras_for_role(self, role: Union[str, "Role"]):
        mw_instance = self.__get_mw_for_role(role)
        return mw_instance.get_extras()
    
    def delete_extras_for_role(self, role: Union[str, "Role"]):
        self.__get_mw_for_role(role).delete_extras()

    
    def delete_role(self, role: Union[str, "Role"]):
        mw_instance = self.__get_mw_for_role(role)
        mw_instance.delete()
    
    def get_related_extras(self):
        res = {}
        try:
            w = self.related_workers
            res["Worker"] = w.pk
        except:
            pass
        try:
            h = self.related_hrs
            res["HR"] = h.pk
        except:
            pass
        if "Moderator" in self.roles.values_list("name", flat=True):
            res["Moderator"] = 1
        return res


class SavedUsers(models.Model):
    owner = models.ForeignKey(to="User", on_delete=models.CASCADE, related_name="related_saved_users")
    saved = models.ForeignKey(to="User", on_delete=models.CASCADE, related_name="related_saved_by")
    description = models.CharField(max_length=2048)

    def __str__(self):
        return f"{self.owner} saved {self.saved}"


class Role(models.Model):
    name = models.CharField(max_length=32)
    extras_content_type = models.ForeignKey(to=ContentType, related_name="ct_roles", on_delete=models.CASCADE, null=True, blank=True)

    objects = RoleManager()


class users_roles(models.Model):
    user = models.ForeignKey(to="User", on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(to="Role", on_delete=models.CASCADE, related_name="role_users")

    def get_extras(self):
        try:
            extras_model = self.role.extras_content_type.model_class()
            return extras_model.objects.get(user=self.user)
        except extras_model.DoesNotExist:
            raise ValueError("This role is not bound, you might use set_extras before")
    
    def delete_extras(self):
        e_model = self.role.extras_content_type.model_class()
        e_model.objects.get(user=self.user).delete()
    
    def delete(self, *args, **kwargs):
        try:
            e_model = self.role.extras_content_type.model_class()
            e_model.objects.get(user=self.user).delete()
        except e_model.DoesNotExist:
            pass
        return super().delete(*args, **kwargs)

    class Meta:
        unique_together = ("user", "role")  # preventing adding same role 


class GenericExtras(models.Model):

    def get_related_user(self):
        try:
            return self.user
        except IndexError:  # artifact
            raise ValueError("Extras instance is not bound")

    class Meta:
        abstract=True


class WorkerExtras(GenericExtras):
    requirements = models.ManyToManyField(to="Requirements", through="requirement_workers", through_fields=("worker", "requirement"))
    skills = models.ManyToManyField(to="Skills", through="skills_workers", through_fields=("worker", "skill"))
    user = models.OneToOneField(to=User, related_name="related_workers", on_delete=models.CASCADE)
    cv = models.FileField(upload_to="media/cvs", null=True, blank=True)

    def add_requirement(self, req_instance: "Requirements", options: Union[List["RequirementOptions"], Tuple["RequirementOptions"]]=[], custom_answer: str=None):
        mw_instance = requirement_workers.objects.create(worker=self, requirement=req_instance)

        for option in options:
            if option.requirement != req_instance:
                raise TypeError(f"Requirement type is incompatible with option type")
        if options:
            for option in options:
                mw_instance.multiple_options.add(option)
        if custom_answer:
            mw_instance.custom_answer = custom_answer
            mw_instance.save()
    
    def get_requirements(self):
        return requirement_workers.objects.prefetch_related("related_mro").filter(worker=self)

    def get_skills(self):
        return skills_workers.objects.filter(worker=self).select_related("skill")
    
    def add_skill(self, skill:Union[str, "Skills"], experience_duration: str=None, experience_level: str=None, description: str=None):
        if type(skill) is str:
            skill = Skills.objects.get(name=skill)
        skills_workers.objects.create(worker=self, skill=skill, experience_duration=experience_duration, experience_level=experience_level, description=description)
    
    def delete_skill(self, skill: Union[str, "Skills"]):
        if type(skill) is str:
            skills_workers.objects.select_related("skill").get(skill__name=skill, worker=self).delete()
        else:
            skills_workers.objects.get(worker=self, skill=skill).delete()

    def get_vacancy_responses(self):
        return vacancy_responses.objects.filter(worker=self).select_related("vacancy")
    
    def respond_to_vacancy(self, vacancy:Union[int, "Vacancy"]):
        if type(vacancy) is str:
            try:
                vacancy = Vacancy.objects.get(pk=vacancy)
            except Vacancy.DoesNotExist:
                raise ValueError("Such vacancy does not exists")
        
        status = VacancyResponseStatuses.objects.get(name="Created")
        vacancy_responses.objects.create(vacancy=vacancy, worker=self, status=status)


class HRExtras(GenericExtras):
    companies = models.ManyToManyField(to="Companies", through="company_hrs", through_fields=("hr", "company"))
    user = models.OneToOneField(to=User, related_name="related_hrs", on_delete=models.CASCADE)

    def create_vacancy(self, title):
        return Vacancy.objects.create(title=title, hr=self)

    def get_vacancies(self):
        return Vacancy.objects.filter(hr=self)

    def delete_vacancy(self, vacancy: "Vacancy"):
        if vacancy.hr == self:
            vacancy.delete()
        else:
            raise ValueError(f"Vacancy to be deleted is not owned by {self}")


class Companies(models.Model):
    name = models.CharField(max_length=32 ,unique=True)


class company_hrs(models.Model): # idea add stage in company
    company = models.ForeignKey(to="Companies", on_delete=models.CASCADE, related_name="related_ch")
    hr = models.ForeignKey(to="HRExtras", on_delete=models.CASCADE, related_name="related_ch")

#  ------------------------requirements-----------------------------

class RequirementTypes(models.Model):
    name = models.CharField(max_length=32)

    objects = RequirementTypesManager()


class Requirements(models.Model):  # TODO merge same requirements
    name = models.CharField(max_length=32)
    requirement_type = models.ForeignKey(to="RequirementTypes", on_delete=models.CASCADE, related_name="related_requirements")
    multiple_answers = models.BooleanField(default=False)

    objects = RequirementsManager()

    def get_options(self):
        return RequirementOptions.objects.filter(requirement=self)
    
    def __str__(self):
        return self.name


class requirement_workers(models.Model):
    worker = models.ForeignKey(to="WorkerExtras", on_delete=models.CASCADE, related_name="related_rw")
    requirement = models.ForeignKey(to="Requirements", on_delete=models.CASCADE, related_name="related_rw")
    custom_answer = models.CharField(max_length=128, null=True, blank=True)
    multiple_options = models.ManyToManyField(to="RequirementOptions", through="multiple_requirement_options", through_fields=("rw", "option"))

    def get_options(self):  # TODO migrate method to serializers
        if self.custom_answer:
            return {"type": "custom", "value": [self.custom_answer]}
        else:  # must prefetch related_mro
            value = [i.value for i in self.multiple_options.all()]
            if len(value) == 1:
                return {"type": "single", "value": value}
            elif len(value) == 0:
                return {"type": "none"}
            return {"type": "multiple", "value": value}


class RequirementOptions(models.Model):
    requirement = models.ForeignKey(to="Requirements", on_delete=models.CASCADE, related_name="related_options")
    value = models.CharField(max_length=32)

    objects = RequirementOptionsManager()


class multiple_requirement_options(models.Model):
    rw = models.ForeignKey(to="requirement_workers", on_delete=models.CASCADE, related_name="related_mro")
    option = models.ForeignKey(to="RequirementOptions", on_delete=models.CASCADE, related_name="related_mro")
    
# --------------------------complains--------------------------------

class ComplainReasons(models.Model):
    name = models.CharField(max_length=32)
    priority = models.PositiveIntegerField(default=0)

    objects = ComplainReasonsManager()


class Complains(models.Model):
    complied = models.ForeignKey(to="User", on_delete=models.CASCADE, related_name="related_complains")
    complier = models.ForeignKey(to="User", on_delete=models.CASCADE, related_name="related_complains_left")
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    reason = models.ForeignKey(to="ComplainReasons", on_delete=models.CASCADE)
    target_type = models.CharField(max_length=32, null=True, blank=True, choices=[
        ("Profile", "Profile"),
        ("Vacancy", "Vacancy"),
    ])
    target_pk = models.PositiveIntegerField(null=True, blank=True)
    screenshot = models.ImageField(upload_to="complains", null=True, blank=True)
    status = models.CharField(max_length=32, default="Pending", choices=[
        ("Pending", "Pending"),
        ("Resolved", "Resolved"),
        ("Closed", "Closed"),
    ])


#-------------------------skills--------------------------------
class Skills(models.Model):
    name = models.CharField(max_length=128)
    tags = models.ManyToManyField(to="SkillTags", through="skills_tags", through_fields=("skill", "tag"))

    objects = SkillsManager()

    def add_tag(self, tag:Union[str, "SkillTags"]):
        if type(tag) is str:
            tag = SkillTags.objects.get(name=tag)
        self.tags.add(tag)
    
    def add_tags(self, tags: Union[List[str], List["SkillTags"]]):
        for tag in tags:
            self.add_tag(tag)
        

class SkillTags(models.Model):
    name = models.CharField(max_length=32)

    objects = SkillTagsManager()


class skills_tags(models.Model):
    skill = models.ForeignKey(to="Skills", on_delete=models.CASCADE, related_name="related_st")
    tag = models.ForeignKey(to="SkillTags", on_delete=models.CASCADE, related_name="related_st")


class skills_workers(models.Model):
    skill = models.ForeignKey(to="Skills", on_delete=models.CASCADE, related_name="related_sw")
    worker = models.ForeignKey(to="WorkerExtras", on_delete=models.CASCADE, related_name="related_sw")
    experience_duration = models.CharField(max_length=32, null=True, blank=True)
    experience_level = models.CharField(max_length=32, null=True, blank=True, choices=[
        ("Trainee", "Trainee"),
        ("Junior", "Junior"),
        ("Middle", "Middle"),
        ("Senior", "Senior")
    ])
    description = models.CharField(max_length=1024, null=True, blank=True)


#-------------------------vacancy--------------------------
class Vacancy(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    hr = models.ForeignKey(to="HRExtras", on_delete=models.CASCADE, related_name="related_vacancies")
    visible = models.BooleanField(default=False)
    skills = models.ManyToManyField(to="Skills", through="vacancy_skills", through_fields=["vacancy", "skill"])

    def add_requirement(self, req_instance: "Requirements", options: Union[List["RequirementOptions"], Tuple["RequirementOptions"]]=[], custom_answer: str=None):
        mw_instance = vacancy_requirements.objects.create(vacancy=self, requirement=req_instance)

        for option in options:
            if option.requirement != req_instance:
                raise TypeError(f"Requirement type is incompatible with option type")
        if options:
            for option in options:
                mw_instance.multiple_options.add(option)
        if custom_answer:
            mw_instance.custom_answer = custom_answer
            mw_instance.save()
    
    def get_requirements(self):
        return vacancy_requirements.objects.prefetch_related("related_vmo").filter(vacancy=self)

    def get_skills(self):
        return vacancy_skills.objects.filter(vacancy=self).select_related("skill")
    
    def add_skill(self, skill:Union[str, "Skills"], experience_duration: str=None, experience_level: str=None, description: str=None):
        if type(skill) is str:
            skill = Skills.objects.get(name=skill)
        vacancy_skills.objects.create(vacancy=self, skill=skill, experience_duration=experience_duration, experience_level=experience_level, description=description)
    
    def delete_skill(self, skill: Union[str, "Skills"]):
        if type(skill) is str:
            vacancy_skills.objects.select_related("skill").get(skill__name=skill, vacancy=self).delete()
        else:
            vacancy_skills.objects.get(vacancy=self, skill=skill).delete()

    def get_vacancy_responses(self):
        return vacancy_responses.objects.filter(vacancy=self).select_related("worker")

    def get_quick_responses(self): 
        return VacancyQuickResponses.objects.filter(vacancy=self).select_related("related_status")

    @staticmethod
    def __fetch_status(status):
        if type(status) is str:
            try:
                status = VacancyResponseStatuses.objects.get(name=status)
            except VacancyResponseStatuses.DoesNotExist:
                raise ValueError(f"Status with name {status} does not exists")
        return status


    def add_quick_response(self, status:Union[str, "VacancyResponseStatuses"], name:str, text:str):
        status = self.__fetch_status(status)
        return VacancyQuickResponses.objects.create(vacancy=self, name=name, response_text=text, related_status=status)
        

    def delete_quick_response(self, status:Union[str, "VacancyResponseStatuses"], name:str):
        status = self.__fetch_status(status)
        ob = VacancyQuickResponses.objects.get(related_status=status, name=name)
        ob.delete()


class vacancy_skills(models.Model):
    skill = models.ForeignKey(to="Skills", on_delete=models.CASCADE, related_name="related_vs")
    vacancy = models.ForeignKey(to="Vacancy", on_delete=models.CASCADE, related_name="related_vs")
    experience_duration = models.CharField(max_length=32, null=True, blank=True)
    experience_level = models.CharField(max_length=32, null=True, blank=True, choices=[
        ("Trainee", "Trainee"),
        ("Junior", "Junior"),
        ("Middle", "Middle"),
        ("Senior", "Senior")
    ])
    relevance = models.PositiveIntegerField(default=1)
    description = models.CharField(max_length=1024, null=True, blank=True)


class vacancy_requirements(models.Model):
    vacancy = models.ForeignKey(to="Vacancy", on_delete=models.CASCADE, related_name="related_vr")
    requirement = models.ForeignKey(to="Requirements", on_delete=models.CASCADE, related_name="related_vr")
    custom_answer = models.CharField(max_length=256, null=True, blank=True)
    multiple_options = models.ManyToManyField(to="RequirementOptions", through="vacancy_multiple_options", through_fields=("vr", "option"))

    def get_options(self):  
        if self.custom_answer:
            return {"type": "custom", "value": [self.custom_answer]}
        else:  # must prefetch related_mro
            value = [i.value for i in self.multiple_options.all()]
            if len(value) == 1:
                return {"type": "single", "value": value}
            elif len(value) == 0:
                return {"type": "none"}
            return {"type": "multiple", "value": value}


class vacancy_multiple_options(models.Model):
    vr = models.ForeignKey(to="vacancy_requirements", on_delete=models.CASCADE, related_name="related_vmo")
    option = models.ForeignKey(to="RequirementOptions", on_delete=models.CASCADE, related_name="related_vmo")


class VacancyResponseStatuses(models.Model):
    name = models.CharField(max_length=128)

    objects = VacancyResponseStatusManager()


class VacancyQuickResponses(models.Model):
    name = models.CharField(max_length=128)
    response_text = models.TextField()
    related_status = models.ForeignKey(to="VacancyResponseStatuses", on_delete=models.CASCADE, related_name="related_quick_responses")
    vacancy = models.ForeignKey(to="Vacancy", on_delete=models.CASCADE, related_name="related_quick_responses")


class vacancy_responses(models.Model): 
    worker = models.ForeignKey(to="WorkerExtras", on_delete=models.CASCADE, related_name="related_responses")
    vacancy = models.ForeignKey(to="Vacancy", on_delete=models.CASCADE, related_name="related_responses")
    creation_date = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(to="VacancyResponseStatuses", on_delete=models.CASCADE, related_name="related_responses")


class SavedVacancies(models.Model):
    owner = models.ForeignKey(to="WorkerExtras", on_delete=models.CASCADE, related_name="related_saved_vacancies")
    vacancy = models.ForeignKey(to="Vacancy", on_delete=models.CASCADE, related_name="related_saved_by")

    def __str__(self):
        return f"{self.owner} saved {self.vacancy}"