from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from complaints.models import District, PradeshiyaSabha, Wasama, OfficerProfile, Complaint, ComplaintRemark
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Populates the database with mock districts, sabhas, wasamas, users, and sample complaints.'

    def handle(self, *args, **options):
        self.stdout.write('Populating mock data...')

        # 1. Create Districts
        districts_data = ['Colombo', 'Kandy', 'Galle']
        districts = {}
        for d_name in districts_data:
            d, created = District.objects.get_or_create(name=d_name)
            districts[d_name] = d
            if created:
                self.stdout.write(f'Created District: {d_name}')

        # 2. Create Pradeshiya Sabhas
        sabhas_data = {
            'Colombo': ['Kaduwela PS', 'Homagama PS'],
            'Kandy': ['Harispattuwa PS', 'Kundasale PS'],
            'Galle': ['Hikkaduwa PS', 'Bope-Poddala PS']
        }
        sabhas = {}
        for d_name, s_list in sabhas_data.items():
            district = districts[d_name]
            sabhas[d_name] = {}
            for s_name in s_list:
                s, created = PradeshiyaSabha.objects.get_or_create(name=s_name, district=district)
                sabhas[d_name][s_name] = s
                if created:
                    self.stdout.write(f'Created Pradeshiya Sabha: {s_name} in {d_name}')

        # 3. Create Wasamas (GN Divisions)
        wasamas_data = {
            'Kaduwela PS': [('Battaramulla South', 'GN 600'), ('Koswatta', 'GN 601'), ('Thalahena', 'GN 602')],
            'Homagama PS': [('Homagama Town', 'GN 580'), ('Pannipitiya', 'GN 581')],
            'Harispattuwa PS': [('Harispattuwa North', 'GN 401'), ('Harispattuwa South', 'GN 402')],
            'Kundasale PS': [('Kundasale Town', 'GN 415'), ('Tennekumbura', 'GN 416')],
            'Hikkaduwa PS': [('Hikkaduwa Town', 'GN 700'), ('Hiranwatta', 'GN 701')],
            'Bope-Poddala PS': [('Bope North', 'GN 720'), ('Poddala East', 'GN 721')]
        }
        wasamas = {}
        for s_name, w_list in wasamas_data.items():
            # Find the sabha
            sabha = None
            for d_name in sabhas:
                if s_name in sabhas[d_name]:
                    sabha = sabhas[d_name][s_name]
                    break
            wasamas[s_name] = []
            for w_name, w_code in w_list:
                w, created = Wasama.objects.get_or_create(name=w_name, code=w_code, pradeshiya_sabha=sabha)
                wasamas[s_name].append(w)
                if created:
                    self.stdout.write(f'Created Wasama: {w_name} ({w_code}) in {s_name}')

        # 4. Create Users and Officer Profiles
        # Admin User
        admin_user, created = User.objects.get_or_create(username='admin', email='admin@ccms.gov.lk')
        if created:
            admin_user.set_password('admin123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            OfficerProfile.objects.create(user=admin_user, role='ADMIN')
            self.stdout.write('Created Superuser/Admin: admin / admin123')
        else:
            # Ensure profile exists
            OfficerProfile.objects.get_or_create(user=admin_user, role='ADMIN')

        # Officer 1 - Colombo/Kaduwela PS assigned
        off_col, created = User.objects.get_or_create(username='officer_colombo', email='colombo@ccms.gov.lk')
        if created:
            off_col.set_password('officer123')
            off_col.save()
            OfficerProfile.objects.create(
                user=off_col,
                role='OFFICER',
                assigned_district=districts['Colombo'],
                assigned_pradeshiya_sabha=sabhas['Colombo']['Kaduwela PS']
            )
            self.stdout.write('Created Officer: officer_colombo / officer123')
        
        # Officer 2 - Kandy/Harispattuwa assigned
        off_kan, created = User.objects.get_or_create(username='officer_kandy', email='kandy@ccms.gov.lk')
        if created:
            off_kan.set_password('officer123')
            off_kan.save()
            OfficerProfile.objects.create(
                user=off_kan,
                role='OFFICER',
                assigned_district=districts['Kandy'],
                assigned_pradeshiya_sabha=sabhas['Kandy']['Harispattuwa PS']
            )
            self.stdout.write('Created Officer: officer_kandy / officer123')

        # Officer 3 - Battaramulla specific GN division assigned
        off_bat, created = User.objects.get_or_create(username='officer_battaramulla', email='battaramulla@ccms.gov.lk')
        if created:
            off_bat.set_password('officer123')
            off_bat.save()
            # Battaramulla South is the first GN division in Kaduwela PS list
            gn_bat = wasamas['Kaduwela PS'][0]
            OfficerProfile.objects.create(
                user=off_bat,
                role='OFFICER',
                assigned_district=districts['Colombo'],
                assigned_pradeshiya_sabha=sabhas['Colombo']['Kaduwela PS'],
                assigned_wasama=gn_bat
            )
            self.stdout.write('Created Officer: officer_battaramulla / officer123')

        # 5. Create Sample Complaints
        complaints_samples = [
            {
                'citizen_name': 'Kamal Perera',
                'citizen_email': 'kamal@gmail.com',
                'citizen_phone': '0771234567',
                'category': 'ROAD_DAMAGE',
                'title': 'Huge Pothole on Battaramulla Main Road',
                'description': 'There is a massive pothole near the Koswatta junction on the main road. It is highly dangerous for motorcycles and has already caused two minor accidents. Please repair it immediately.',
                'district_name': 'Colombo',
                'sabha_name': 'Kaduwela PS',
                'wasama_idx': 0, # Battaramulla South
                'status': 'PENDING',
            },
            {
                'citizen_name': 'Nimal Silva',
                'citizen_email': 'nimal@yahoo.com',
                'citizen_phone': '0719876543',
                'category': 'WASTE_MGMT',
                'title': 'Uncollected Garbage in Thalahena Area',
                'description': 'Garbage has not been collected in our street (3rd lane, Thalahena) for over a week. The smell is unbearable and stray dogs are scattering the waste everywhere. This is a severe health risk.',
                'district_name': 'Colombo',
                'sabha_name': 'Kaduwela PS',
                'wasama_idx': 2, # Thalahena
                'status': 'IN_PROGRESS',
                'remarks': [
                    ('officer_colombo', 'Inspected the site. Notified the waste management contractor to dispatch a collection truck tomorrow morning.', 'PENDING', 'IN_PROGRESS')
                ]
            },
            {
                'citizen_name': 'Sunil Fernando',
                'citizen_email': 'sunil@outlook.com',
                'citizen_phone': '0761112223',
                'category': 'DRAINAGE',
                'title': 'Blocked Drainage causing minor flooding',
                'description': 'The storm drain opposite Homagama Primary School is completely blocked with plastic bottles and silt. When it rains, the water overflows onto the school entrance walkway.',
                'district_name': 'Colombo',
                'sabha_name': 'Homagama PS',
                'wasama_idx': 0, # Homagama Town
                'status': 'PENDING',
            },
            {
                'citizen_name': 'Chathuri Alwis',
                'citizen_email': 'chathuri@gmail.com',
                'citizen_phone': '0723334445',
                'category': 'STREET_LIGHT',
                'title': 'Broken Street Lights near Harispattuwa Junction',
                'description': 'Three street lights have been burned out for more than two weeks near the main junction. It gets completely dark after 6:30 PM, making it unsafe for residents walking home.',
                'district_name': 'Kandy',
                'sabha_name': 'Harispattuwa PS',
                'wasama_idx': 0, # Harispattuwa North
                'status': 'RESOLVED',
                'remarks': [
                    ('officer_kandy', 'Logged request with the electrical maintenance team.', 'PENDING', 'IN_PROGRESS'),
                    ('officer_kandy', 'Bulbs replaced and lighting restored. Verified operation tonight.', 'IN_PROGRESS', 'RESOLVED')
                ]
            },
            {
                'citizen_name': 'Ruwan Kumara',
                'citizen_email': 'ruwan@outlook.com',
                'citizen_phone': '0758889990',
                'category': 'ENVIRONMENT',
                'title': 'Illegal Dumping near Hikkaduwa Beach Access Road',
                'description': 'Some local hotels are dumping wastewater and dry waste in the vacant lot near the beach access lane. The environmental impact is bad and tourists are complaining.',
                'district_name': 'Galle',
                'sabha_name': 'Hikkaduwa PS',
                'wasama_idx': 0, # Hikkaduwa Town
                'status': 'REJECTED',
                'remarks': [
                    ('admin', 'Dumping ground is on private property. The owner has been sent a warning notice directly. Closing ticket as it is outside public council authority but direct enforcement is active.', 'PENDING', 'REJECTED')
                ]
            },
            {
                'citizen_name': 'Anura Bandara',
                'citizen_email': 'anura@gmail.com',
                'citizen_phone': '0779998887',
                'category': 'PUBLIC_SVC',
                'title': 'Delay in issuing local building permit approval',
                'description': 'Submitted building plans over two months ago at Bope-Poddala Pradeshiya Sabha office. Followed up twice, but officers keep stating the files are pending review. Need urgent attention.',
                'district_name': 'Galle',
                'sabha_name': 'Bope-Poddala PS',
                'wasama_idx': 0, # Bope North
                'status': 'IN_PROGRESS',
                'remarks': [
                    ('admin', 'Forwarded to the planning committee supervisor. Review scheduled for the weekly meeting.', 'PENDING', 'IN_PROGRESS')
                ]
            }
        ]

        # Prevent duplicate complaints on repeated runs
        if Complaint.objects.count() == 0:
            for c_data in complaints_samples:
                dist = districts[c_data['district_name']]
                sabha = sabhas[c_data['district_name']][c_data['sabha_name']]
                wasama = wasamas[c_data['sabha_name']][c_data['wasama_idx']]

                complaint = Complaint.objects.create(
                    citizen_name=c_data['citizen_name'],
                    citizen_email=c_data['citizen_email'],
                    citizen_phone=c_data['citizen_phone'],
                    category=c_data['category'],
                    title=c_data['title'],
                    description=c_data['description'],
                    district=dist,
                    pradeshiya_sabha=sabha,
                    wasama=wasama,
                    status=c_data['status']
                )
                self.stdout.write(f"Created Complaint {complaint.reference_number}: {complaint.title}")

                # Add remarks if any
                if 'remarks' in c_data:
                    for off_username, rem_text, s_from, s_to in c_data['remarks']:
                        user = User.objects.get(username=off_username)
                        ComplaintRemark.objects.create(
                            complaint=complaint,
                            officer=user,
                            remark=rem_text,
                            status_from=s_from,
                            status_to=s_to
                        )
                        self.stdout.write(f"  Added Remark: {rem_text[:30]}...")
            self.stdout.write('Mock complaints successfully populated!')
        else:
            self.stdout.write('Complaints already exist in database, skipping populating complaints.')

        self.stdout.write('Mock populating complete!')
