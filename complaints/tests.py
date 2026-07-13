from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from complaints.models import District, PradeshiyaSabha, Wasama, Complaint, OfficerProfile
import json

class ComplaintSystemTests(TestCase):
    def setUp(self):
        # 1. Create Location Hierarchy
        self.district = District.objects.create(name="Colombo")
        self.sabha = PradeshiyaSabha.objects.create(name="Kaduwela PS", district=self.district)
        self.wasama = Wasama.objects.create(name="Battaramulla", code="GN 600", pradeshiya_sabha=self.sabha)
        
        # 2. Create Users
        # Admin
        self.admin_user = User.objects.create_user(username="admin_test", password="password123")
        OfficerProfile.objects.create(user=self.admin_user, role='ADMIN')
        
        # Officer assigned to Colombo district
        self.officer_user = User.objects.create_user(username="officer_test", password="password123")
        OfficerProfile.objects.create(
            user=self.officer_user, 
            role='OFFICER', 
            assigned_district=self.district,
            assigned_pradeshiya_sabha=self.sabha
        )
        
        self.client = Client()

    def test_reference_number_generation(self):
        # Verify that reference number is generated on Complaint save
        complaint = Complaint.objects.create(
            citizen_name="Test Citizen",
            citizen_email="test@citizen.com",
            citizen_phone="0777777777",
            category="ROAD_DAMAGE",
            title="Pothole in test road",
            description="Detailed test description",
            district=self.district,
            pradeshiya_sabha=self.sabha,
            wasama=self.wasama
        )
        
        self.assertIsNotNone(complaint.reference_number)
        self.assertTrue(complaint.reference_number.startswith("CCMS-"))
        self.assertEqual(len(complaint.reference_number), 15) # CCMS-2026-XXXXX (5 + 4 + 1 + 5 = 15 chars)

    def test_ajax_get_sabhas(self):
        # Verify AJAX api returns correct sabhas under the district
        url = reverse('api_get_sabhas')
        response = self.client.get(url, {'district_id': self.district.id})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Kaduwela PS")

    def test_ajax_get_wasamas(self):
        # Verify AJAX api returns correct wasamas under the sabha
        url = reverse('api_get_wasamas')
        response = self.client.get(url, {'sabha_id': self.sabha.id})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Battaramulla")

    def test_unauthenticated_dashboard_redirect(self):
        # Verify that accessing dashboards without login redirects to login page
        urls = [
            reverse('officer_dashboard'),
            reverse('admin_dashboard'),
            reverse('dashboard_router')
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertTrue('/login/' in response.url)

    def test_authorized_officer_dashboard_access(self):
        # Verify that authenticated officer can access officer dashboard but not admin dashboard
        self.client.login(username="officer_test", password="password123")
        
        # Officer dashboard should load fine
        response = self.client.get(reverse('officer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "officer_test")
        
        # Admin dashboard should redirect officer with error message
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('officer_dashboard'))

    def test_authorized_admin_dashboard_access(self):
        # Verify that authenticated admin can access admin dashboard and gets redirected from router
        self.client.login(username="admin_test", password="password123")
        
        # Router should redirect admin to admin dashboard
        response = self.client.get(reverse('dashboard_router'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin_dashboard'))
        
        # Admin dashboard should load
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "admin_test")
