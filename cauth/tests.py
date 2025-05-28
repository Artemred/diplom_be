from django.test import TestCase, TransactionTestCase, Client
from .models import Role, User, WorkerExtras, HRExtras, users_roles, RequirementTypes, Requirements, RequirementOptions, Companies, ComplainReasons, Complains, Skills, SkillTags, Vacancy, requirement_workers, vacancy_requirements, skills_workers, fill_db, VacancyResponseStatuses, vacancy_responses, VacancyQuickResponses
from django.db.utils import IntegrityError
from rest_framework.authtoken.models import Token

#testing aviability of data in db
class UserTestCase(TransactionTestCase):  # transaction test case because general one cant close broken transaction
    def setUp(self):
        fill_db()
        User.objects.create(username="u1")
    
    def test_generated_roles(self):
        self.assertEqual(len(Role.objects.all()), 2)
    
    def test_role_add(self):
        u = User.objects.get(username="u1")
        u.add_role("HR")
        self.assertEqual(len(u.roles.all()), 1)  # general
        with self.assertRaises(IntegrityError):  # attempt to add same role
            u.add_role("HR")
        with self.assertRaises(Role.DoesNotExist):  # attempt to add not existing role
            u.add_role("wee")
    
    def test_role_extras(self):
        u = User.objects.get(username="u1")
        u.add_role("HR")
        extras = u.get_extras_for_role("HR")
        self.assertEqual(u.get_extras_for_role("HR").__class__, HRExtras)
        with self.assertRaises(users_roles.DoesNotExist):  # attempt to get extras for not owned role
            u.get_extras_for_role("Worker")
        u.add_role("Worker")
        u.delete_extras_for_role("Worker")
        with self.assertRaises(ValueError):  # attempt to get not bound role extras
            u.get_extras_for_role("Worker")
    
    def test_role_deletion(self):
        u = User.objects.get(username="u1")
        u.add_role("HR")
        self.assertEqual(HRExtras.objects.count(), 1)  # after change extras unused instance must be removed
        u.delete_role("HR")
        self.assertEqual(HRExtras.objects.count(), 0)  # after role deletion generic extras object must be deleted
    
    def test_worker_requirements(self):
        u = User.objects.get(username="u1")
        u.add_role("Worker")
        r = Requirements.objects.get(name="Working day")
        self.assertEqual(r.get_options().count(), 3)
        extras = u.get_extras_for_role("Worker")
        ri = Requirements.objects.get(name="Working day")
        sl = Requirements.objects.get(name="Salary")

        extras.add_requirement(ri, custom_answer="0h")
        self.assertEqual(extras.get_requirements()[0].get_options(), {'type': 'custom', 'value': ['0h']})  # test custom requirement creation
        extras.get_requirements()[0].delete()

        rc1 = RequirementOptions.objects.get(requirement=ri, value="8h") 
        rc2 = RequirementOptions.objects.get(requirement=ri, value="6h")
        sl1 = RequirementOptions.objects.get(requirement=sl, value="10")
        extras.add_requirement(ri, options=[rc1, rc2])
        self.assertEqual(extras.get_requirements()[0].get_options(), {'type': 'multiple', 'value': ['8h', '6h']})  # test multiple requirement creation
        extras.get_requirements()[0].delete()

        extras.add_requirement(ri, options=[rc2])
        self.assertEqual(extras.get_requirements()[0].get_options(), {'type': 'single', 'value': ['6h']})  # test single requirement creation

        with self.assertRaises(TypeError):
            extras.add_requirement(ri, options=[sl1])  # test incompatible option and requirement

    def test_hr_companies(self):
        u = User.objects.get(username="u1")
        u.add_role("HR")
        hre = u.get_extras_for_role("HR")
        newcomp = Companies.objects.create(name="Company1")
        hre.companies.add(newcomp)
        self.assertEqual(hre.companies.count(), 1)

    def test_complains(self):
        u1 = User.objects.create(username="u01")
        u2 = User.objects.create(username="u02")
        cr = ComplainReasons.objects.first()
        Complains.objects.create(complied=u1, complier=u2, reason=cr)
        self.assertEqual(Complains.objects.count(), 1)

    def test_skills(self):
        u = User.objects.get(username="u1")
        u.add_role("Worker")
        s = Skills.objects.get(name="Django")
        s2 = Skills.objects.get(name="React")
        self.assertEqual([i.name for i in s.tags.all()], ["Python", "Backend"])  # testing tags of created skills
        we = u.get_extras_for_role("Worker")
        we.add_skill(s, description="im baboon")
        we.add_skill(s2, description="im baboon")
        self.assertEqual(we.skills.get(name="Django"), s)  # testing skill adding
        skill_description = we.get_skills().get(skill__name="Django")
        self.assertEqual(skill_description.skill, s)
        self.assertEqual(skill_description.description, "im baboon")  # testing how correct data is stored
        we.delete_skill("Django")
        self.assertEqual(we.skills.count(), 1)  # testing skill deletion by string
        we.delete_skill(s2)
        self.assertEqual(we.skills.count(), 0)  # testing skill deletion by instance

    def test_vacancies(self):
        u = User.objects.get(username="u1")
        u.add_role("HR")
        u2 = User.objects.create(username="u2")
        u2.add_role("HR")
        he2 = u2.get_extras_for_role("HR")
        he = u.get_extras_for_role("HR")
        vacancy = he.create_vacancy(title="vacancy1")
        self.assertEqual(he.get_vacancies().count(), 1)  # testing creation from hr model
        self.assertEqual(vacancy.hr, he)  # testing vacancy owner
        with self.assertRaises(ValueError):  # testing deletion of not owned vacancy
            he2.delete_vacancy(vacancy)
        
        s = Skills.objects.get(name="Django")
        s2 = Skills.objects.get(name="React")
        v = vacancy
        v.add_skill(s, description="im baboon")
        v.add_skill(s2, description="im baboon")
        self.assertEqual(v.skills.get(name="Django"), s)  # testing skill adding
        skill_description = v.get_skills().get(skill__name="Django")
        self.assertEqual(skill_description.skill, s)
        self.assertEqual(skill_description.description, "im baboon")  # testing how correct data is stored
        v.delete_skill("Django")
        self.assertEqual(v.skills.count(), 1)  # testing skill deletion by string
        v.delete_skill(s2)
        self.assertEqual(v.skills.count(), 0)  # testing skill deletion by instance

        ri = Requirements.objects.get(name="Working day")
        sl = Requirements.objects.get(name="Salary")
        vacancy.add_requirement(ri, custom_answer="0h")
        self.assertEqual(vacancy.get_requirements()[0].get_options(), {'type': 'custom', 'value': ['0h']})  # test custom requirement creation
        vacancy.get_requirements()[0].delete()
        rc1 = RequirementOptions.objects.get(requirement=ri, value="8h") 
        rc2 = RequirementOptions.objects.get(requirement=ri, value="6h")
        sl1 = RequirementOptions.objects.get(requirement=sl, value="10")
        v.add_requirement(ri, options=[rc1, rc2])
        self.assertEqual(v.get_requirements()[0].get_options(), {'type': 'multiple', 'value': ['8h', '6h']})  # test multiple requirement creation
        v.get_requirements()[0].delete()
        v.add_requirement(ri, options=[rc2])
        self.assertEqual(v.get_requirements()[0].get_options(), {'type': 'single', 'value': ['6h']})  # test single requirement creation

        with self.assertRaises(TypeError):
            v.add_requirement(ri, options=[sl1])  # test incompatible option and requirement


class AuthTestCase(TransactionTestCase):
    def setUp(self):
        self.client = Client()

    def test_token_obtain_view(self):
        u = User.objects.create(username="u1")
        u.set_password("Aa111111")
        u.save()
        stored_token = Token.objects.get(user=u).key
        self.assertNotEqual(stored_token, None)  # testing token creation with new user
        res = self.client.post("/api/v1/auth/", data={"username": "u1", "password": "Aa111111"})
        self.assertEqual(res.json()["token"], stored_token)  # testing token, returned from the view

    def test_register_view(self):
        res = self.client.post("/api/v1/auth/register/", data={"username": "u1", "password": "qwe"})
        self.assertEqual(res.status_code, 201)
        res = self.client.post("/api/v1/auth/register/", data={"username": "u1", "password": "qwe"})
        self.assertEqual(res.json(), {'username': 'user with such username already exists'})  # testing repeatable create
        res = self.client.post("/api/v1/auth/register/", data={"input": "baboon"})
        self.assertEqual(res.json(), [{'username': 'this field is required'}, {'password': 'this field is required'}])  # testing readable response in case if fe developer is baboon
        self.assertEqual(User.objects.count(), 1)  # db-side creation
        u = User.objects.first()
        self.assertTrue(u.check_password("qwe"))  # had password been set correctly
    
    def test_occupied_usernames(self):
        User.objects.create(username="u1")
        res = self.client.get("/api/v1/auth/occupied/u1")
        self.assertEqual(res.json(), {"occupied": True})
        res = self.client.get("/api/v1/auth/occupied/u2")
        self.assertEqual(res.json(), {"occupied": False}) 


class ProfileTestCase(TestCase):
    def setUp(self):
        fill_db()
        self.client = Client()
        self.user = User.objects.create(username="u1")
        self.user.add_role("HR")
        self.user.add_role("Worker")
        self.user.email="qwe"
        self.user.save()
        self.user2 = User.objects.create(username="u2")
        self.token = f"Token {Token.objects.get(user=self.user).key}"

    def test_required_auth(self):
        res = self.client.get(f"/api/v1/profile/{self.user.pk}")
        self.assertEqual(res.status_code, 401)  # unauthorized check
        res = self.client.get(f"/api/v1/profile/{self.user.pk}", headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 200)  # authorized check
    
    def test_retrieve_view(self):
        res = self.client.get(f"/api/v1/profile/", headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["email"], "qwe")  # testing own profile 
        res = self.client.get(f"/api/v1/profile/{self.user2.pk}", headers={"Authorization": self.token})
        with self.assertRaises(KeyError):  # testing request for not owned profile
            res.json()["email"]
        res = self.client.get(f"/api/v1/profile/777", headers={"Authorization": self.token})
        self.assertEqual(res.json(), {'error': 'User not found'})  # testing request for not existing user
    
    def test_update_view(self):
        res = self.client.patch(f"/api/v1/profile/{self.user.pk}", headers={"Authorization": self.token}, data={"email": "rty@gmail.com"}, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        u = User.objects.get(pk=self.user.pk)
        self.assertEqual(u.email, "rty@gmail.com")  # testing change of some field
        res = self.client.patch(f"/api/v1/profile/111", headers={"Authorization": self.token}, data={"email": "rty@gmail.com"}, content_type='application/json')
        self.assertEqual(res.json(), {'error': 'Authorized user cant change this profile'})
    
    def test_delete_view(self):
        res = self.client.delete(f"/api/v1/profile/111", headers={"Authorization": self.token})
        self.assertEqual(res.json(), {'error': 'Authorized user cant delete this profile'})  # testing attempt to delete other user
        res = self.client.delete(f"/api/v1/profile/{self.user.pk}", headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 200)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(pk=self.user.pk)


class ExtrasViewsTestCase(TransactionTestCase):
    def setUp(self):
        fill_db()

        self.user = User.objects.create(username="u1")
        self.user.add_role("Worker")
        self.user_extras = self.user.get_extras_for_role("Worker")
        r = Requirements.objects.get(name="Working day")
        s = Skills.objects.get(name="Django")
        self.user_extras.add_skill(s, description="im baboon")
        self.user_extras.add_requirement(r, custom_answer="-1h")

        self.user2 = User.objects.create(username="u2")
        self.user2.add_role("Worker")
        self.user2_extras = self.user2.get_extras_for_role("Worker")
        rc1 = RequirementOptions.objects.get(requirement=r, value="8h") 
        rc2 = RequirementOptions.objects.get(requirement=r, value="6h")
        self.user2_extras.add_requirement(r, options=[rc1, rc2])

        self.user3 = User.objects.create(username="u3")
        self.user3.add_role("HR")
        self.user3_extras = self.user3.get_extras_for_role("HR")
        self.user3_extras.create_vacancy(title="baboon vacancy")

        self.token = f"Token {Token.objects.get(user=self.user).key}"
        self.token3 = f"Token {Token.objects.get(user=self.user3).key}"


        self.client = Client()
    
    def test_workers_extras(self):
        res = self.client.get(f"/api/v1/profile/extras/{self.user.pk}/Worker", headers={"Authorization": self.token})
        self.assertEqual(res.json()["get_requirements"][0]["custom_answer"], "-1h")  # testing custom option serialization
        self.assertEqual(res.json()["get_skills"][0]["description"], "im baboon")  # testing skill serialization
        res = self.client.get(f"/api/v1/profile/extras/{self.user2.pk}/Worker", headers={"Authorization": self.token})
        self.assertEqual(len(res.json()["get_requirements"][0]["multiple_options_details"]), 2)  # testing multiple options serialization
    
    def test_hr_extras(self):
        res = self.client.get(f"/api/v1/profile/extras/{self.user3.pk}/HR", headers={"Authorization": self.token})
        self.assertEqual(res.json()["get_vacancies"][0]["title"], "baboon vacancy")

    def test_worker_requirements(self):
        requirement_workers.objects.filter(worker=self.user_extras).delete()
        requirement = Requirements.objects.get(name="Working day").pk
        o1 = RequirementOptions.objects.filter(requirement__pk=requirement)[0].pk
        o2 = RequirementOptions.objects.filter(requirement__pk=requirement)[1].pk
        res = self.client.post("/api/v1/requirements/worker/", {"requirement": requirement, "multiple_options": [o1, o2]}, headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 201)
        res = self.client.get(f"/api/v1/profile/extras/{self.user.pk}/Worker", headers={"Authorization": self.token})
        self.assertEqual(res.json()["get_requirements"][0]["multiple_options_details"].__len__(), 2)
        pk = res.json()["get_requirements"][0]["pk"]
        res = self.client.post("/api/v1/requirements/worker/", {"requirement": requirement, "multiple_options": [o1, o2]}, headers={"Authorization": self.token3})
        self.assertEqual(res.status_code, 403)  # attempt to add requirement if u are not worker
        res = self.client.delete(f"/api/v1/requirements/worker/{pk}", headers={"Authorization": self.token3})
        self.assertEqual(res.status_code, 403)  # attempt to delete others requirement
        res = self.client.delete(f"/api/v1/requirements/worker/{pk}", headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 200)  # general deletion
        self.assertEqual(self.user_extras.get_requirements().count(), 0)
        res = self.client.delete(f"/api/v1/requirements/worker/{pk}", headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 400)  # attempt to delete same requirement

    def test_worker_skills(self):
        skills_workers.objects.filter(worker=self.user_extras).delete()
        skill = Skills.objects.first()
        res = self.client.post("/api/v1/skills/worker/", {"skill": skill.pk, "description": "im baboon"}, headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 201)
        self.assertEqual(self.user_extras.get_skills().count(), 1)  # testing insertion of new skill
        skill = self.user_extras.get_skills()[0].pk
        res = self.client.delete(f"/api/v1/skills/worker/{skill}", headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.user_extras.get_skills().count(), 0)


class VacancyViewsTestCase(TransactionTestCase):
    def setUp(self):
        fill_db()

        self.user = User.objects.create(username="u1")
        self.user.add_role("HR")
        self.extras = self.user.get_extras_for_role("HR")
        self.client = Client()
        self.token = f"Token {Token.objects.get(user=self.user).key}"
        self.user2 = User.objects.create(username="u2")
        self.token2 = f"Token {Token.objects.get(user=self.user2).key}"

    def test_retrieve(self):
        self.client.post("/api/v1/vacancies/", {"title": "qwe", "description": "rty"}, headers={"Authorization": self.token})  # create vacancy
        vacancy = Vacancy.objects.filter(title="qwe").first()
        requirement = Requirements.objects.get(name="Working day").pk
        o1 = RequirementOptions.objects.filter(requirement__pk=requirement)[0].pk
        o2 = RequirementOptions.objects.filter(requirement__pk=requirement)[1].pk
        self.client.post(f"/api/v1/requirements/vacancy/", {"vacancy": vacancy.pk, "requirement": requirement, "multiple_options": [o1, o2]}, headers={"Authorization": self.token})  # add requirement
        skill = Skills.objects.first().pk
        self.client.post(f"/api/v1/skills/vacancy/", {"vacancy": vacancy.pk, "skill": skill, "description": "baboon required"}, headers={"Authorization": self.token})  # add skill
        
        res = self.client.get(f"/api/v1/vacancies/{vacancy.pk}")
        self.assertEqual(res.json()["get_requirements"][0]["multiple_options_details"].__len__(), 2)  # correct requirements options repr
        self.assertEqual(res.json()["get_skills"].__len__(), 1)  # correct skills repr

    def test_creation(self):
        res = self.client.post("/api/v1/vacancies/", {"title": "qwe", "description": "rty"}, headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 201)  # testing successfull creation
        res = self.client.get(f"/api/v1/vacancies/{Vacancy.objects.first().pk}")
        self.assertEqual(res.json()["hr"], self.extras.pk)  # testing correct owner
        res = self.client.post("/api/v1/vacancies/", {"title": "qwe", "description": "rty"}, headers={"Authorization": self.token2})
        self.assertEqual(res.status_code, 403)  # attempt to create vacancy by non-hr user
        res = self.client.patch(f"/api/v1/vacancies/{Vacancy.objects.first().pk}", {"title": "new"}, headers={"Authorization": self.token}, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        res = self.client.get(f"/api/v1/vacancies/{Vacancy.objects.first().pk}")
        self.assertEqual(res.json()["title"], "new")  # testing change of vacancy
        res = self.client.patch(f"/api/v1/vacancies/{Vacancy.objects.first().pk}", {"title": "new2"}, headers={"Authorization": self.token2}, content_type="application/json")
        self.assertEqual(res.status_code, 403)  # attempt to change vacancy by non-owner
        res = self.client.delete(f"/api/v1/vacancies/{Vacancy.objects.first().pk}", headers={"Authorization": self.token2})
        self.assertEqual(res.status_code, 403)  # attempt to delete by non-owner
        res = self.client.delete(f"/api/v1/vacancies/{Vacancy.objects.first().pk}", headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 200)  # delete by owner
        self.assertEqual(Vacancy.objects.count(), 0)
    
    def test_vacancy_requirements(self):
        self.client.post("/api/v1/vacancies/", {"title": "qwe", "description": "rty"}, headers={"Authorization": self.token})
        vacancy = self.extras.get_vacancies().first()
        requirement = Requirements.objects.get(name="Working day").pk
        o1 = RequirementOptions.objects.filter(requirement__pk=requirement)[0].pk
        o2 = RequirementOptions.objects.filter(requirement__pk=requirement)[1].pk
        res = self.client.post(f"/api/v1/requirements/vacancy/", {"vacancy": vacancy.pk, "requirement": requirement, "multiple_options": [o1, o2]}, headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 201)  # successfull creation
        self.assertEqual(vacancy.get_requirements()[0].multiple_options.all().count(), 2)  # other cases tested with parent view
        res = self.client.delete(f"/api/v1/requirements/vacancy/{vacancy.get_requirements()[0].pk}", headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(vacancy.get_requirements().count(), 0)  # testing successfull deletion

    def test_vacancy_skills(self):
        self.client.post("/api/v1/vacancies/", {"title": "qwe", "description": "rty"}, headers={"Authorization": self.token})
        vacancy = self.extras.get_vacancies().first()
        skill = Skills.objects.first().pk
        res = self.client.post(f"/api/v1/skills/vacancy/", {"vacancy": vacancy.pk, "skill": skill, "description": "baboon required"}, headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 201)  # successfull creation
        self.assertEqual(vacancy.get_skills().count(), 1)  # other cases tested with parent view
        res = self.client.delete(f"/api/v1/skills/vacancy/{vacancy.get_skills()[0].pk}", headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(vacancy.get_requirements().count(), 0)  # testing successfull deletion
    
    def test_list_view(self):
        v1 = self.extras.create_vacancy("title1")
        req = Requirements.objects.get(name="Salary")
        req2 = Requirements.objects.get(name="Working day")
        o2_1 = RequirementOptions.objects.filter(requirement=req2)[0]
        o2_2 = RequirementOptions.objects.filter(requirement=req2)[1]
        v1.add_requirement(req2, options=[o2_1, o2_2])
        v2 = self.extras.create_vacancy("title2")
        v2.add_requirement(req2, options=[o2_1])
        v3 = self.extras.create_vacancy("title3")
        v4 = self.extras.create_vacancy("title12")
        for i in [v1, v2, v3, v4]:
            i.visible = True
            i.save()
        r = self.client.post("/api/v1/vacancies/list/", {"hr": 11})
        self.assertEqual(r.json().__len__(), 0)
        r = self.client.post("/api/v1/vacancies/list/", {"title": 1})
        self.assertEqual(r.json().__len__(), 2)
        r = self.client.post("/api/v1/vacancies/list/", {"title": "tit"})
        self.assertEqual(r.json().__len__(), 4)
        r = self.client.post(f"/api/v1/vacancies/list/", {"requirements": [req.pk, req2.pk]})
        self.assertEqual(r.json().__len__(), 2)

        r = self.client.post(f"/api/v1/vacancies/list/", {"requirements": [req2.pk], "options": [o2_1.pk]})  # 8h
        self.assertEqual(r.json().__len__(), 2)  # testing options
        r = self.client.post(f"/api/v1/vacancies/list/", {"requirements": [req2.pk], "options": [o2_2.pk]})  # 6h
        self.assertEqual(r.json().__len__(), 1)


class OtherViewsTestCase(TransactionTestCase):
    def setUp(self):
        fill_db()
        
        self.client = Client()
        self.hr = User.objects.create(username="hr")
        self.hre = self.hr.add_role("HR")
        self.vacancy = self.hre.create_vacancy(title="vacancy1")
        self.w = User.objects.create(username="wo")
        self.we = self.w.add_role("Worker")
    
    def test_requirements_list(self):
        res = self.client.get("/api/v1/requirements/list/Worker/")
        self.assertGreaterEqual(res.json().__len__(), 2)
        for i in res.json():
            self.assertEqual(i["requirement_type"]["name"], "Both")
        res = self.client.get("/api/v1/requirements/list/Vacancy/")
        self.assertGreaterEqual(res.json().__len__(), 2)
        for i in res.json():
            self.assertEqual(i["requirement_type"]["name"], "Both")  # testing filtering by type
        
        res = self.client.get("/api/v1/requirements/list/Worker/sal")  # testing filtering by name part
        self.assertEqual(res.json()[0]["name"], "Salary")
    
    def test_skills_list(self):
        res = self.client.get("/api/v1/skills/list/")
        amm = len(res.json())
        self.assertGreater(amm, 1)
        res = self.client.get("/api/v1/skills/list/dja")
        self.assertGreater(amm, res.json().__len__()) 
    
    def test_requirement_options(self):
        requirement = Requirements.objects.get(name="Working day")
        res = self.client.get(f"/api/v1/requirements/options/{requirement.pk}")
        self.assertGreater(len(res.json()), 2)
    
    def test_vacancy_responses(self):
        self.we.respond_to_vacancy(self.vacancy)
        self.assertEqual(self.we.get_vacancy_responses().count(), 1)  # testing storage of created response from worker
        self.assertQuerySetEqual(self.vacancy.get_vacancy_responses(), self.we.get_vacancy_responses())  # testing storage of created response from vacancy(hr)
    
    def test_quick_responses(self):
        self.vacancy.add_quick_response(status="Created", name="name1", text="text1")
        self.vacancy.add_quick_response(status="Created", name="name2", text="text2")
        self.assertEqual([i.response_text for i in self.vacancy.get_quick_responses()], ["text1", "text2"])

        self.vacancy.delete_quick_response(status="Created", name="name1")
        self.assertEqual([i.response_text for i in self.vacancy.get_quick_responses()], ["text2"])
