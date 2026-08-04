from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Count, Q
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _
from .models import District, PradeshiyaSabha, Wasama, OfficerProfile, Complaint, ComplaintRemark
from .forms import ComplaintForm, OfficerRemarkForm

def index(request):
    # Public index / landing page
    if request.method == 'POST':
        # Quick tracking search
        ref = request.POST.get('reference_number', '').strip()
        if ref:
            if Complaint.objects.filter(reference_number=ref).exists():
                return redirect('track_complaint', ref_num=ref)
            else:
                messages.error(request, _("No complaint found with Reference Number '%(ref)s'. Please check and try again.") % {'ref': ref})
    return render(request, 'index.html')

def lodge_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save()
            messages.success(request, _("Complaint submitted successfully! Your Reference Number is %(reference)s.") % {'reference': complaint.reference_number})
            return render(request, 'lodge_success.html', {'complaint': complaint})
        else:
            messages.error(request, _('There was an error submitting your complaint. Please correct the fields below.'))
    else:
        form = ComplaintForm()
    
    districts = District.objects.all()
    return render(request, 'lodge_complaint.html', {'form': form, 'districts': districts})

def track_complaint(request, ref_num):
    complaint = get_object_or_404(Complaint, reference_number=ref_num)
    remarks = complaint.remarks.all()
    return render(request, 'track.html', {'complaint': complaint, 'remarks': remarks})

def translate_place_name(name):
    if not name:
        return ""
    trans = str(_(name))
    if trans != name:
        return trans
    res = name
    replacements = [
        ("Pradeshiya Sabha", str(_("Pradeshiya Sabha"))),
        ("Municipal Council", str(_("Municipal Council"))),
        ("Urban Council", str(_("Urban Council"))),
        ("North", str(_("North"))),
        ("South", str(_("South"))),
        ("East", str(_("East"))),
        ("West", str(_("West"))),
        ("Central", str(_("Central"))),
        ("Town", str(_("Town"))),
    ]
    for eng, tr in replacements:
        if eng in res:
            res = res.replace(eng, tr)
    return res

# AJAX Cascading boundaries APIs
def get_sabhas(request):
    district_id = request.GET.get('district_id')
    sabhas = PradeshiyaSabha.objects.filter(district_id=district_id)
    data = [{'id': s.id, 'name': translate_place_name(s.name)} for s in sabhas]
    return JsonResponse(data, safe=False)

def get_wasamas(request):
    sabha_id = request.GET.get('sabha_id')
    wasamas = Wasama.objects.filter(pradeshiya_sabha_id=sabha_id)
    data = [{'id': w.id, 'name': translate_place_name(w.name), 'code': w.code} for w in wasamas]
    return JsonResponse(data, safe=False)

# Auth dashboard routing
@login_required
def dashboard_router(request):
    try:
        profile = request.user.profile
    except OfficerProfile.DoesNotExist:
        # Create an officer profile if it doesn't exist for some reason
        profile = OfficerProfile.objects.create(user=request.user, role='OFFICER')
    
    if profile.role == 'ADMIN':
        return redirect('admin_dashboard')
    else:
        return redirect('officer_dashboard')

@login_required
def officer_dashboard(request):
    profile = get_object_or_404(OfficerProfile, user=request.user)
    
    # Restrict complaints based on officer's assignment scope
    complaints = Complaint.objects.all()
    
    if profile.assigned_wasama:
        complaints = complaints.filter(wasama=profile.assigned_wasama)
        scope_title = _('Wasama: %(name)s') % {'name': profile.assigned_wasama.name}
    elif profile.assigned_pradeshiya_sabha:
        complaints = complaints.filter(pradeshiya_sabha=profile.assigned_pradeshiya_sabha)
        scope_title = _('Sabha: %(name)s') % {'name': profile.assigned_pradeshiya_sabha.name}
    elif profile.assigned_district:
        complaints = complaints.filter(district=profile.assigned_district)
        scope_title = _('District: %(name)s') % {'name': profile.assigned_district.name}
    else:
        scope_title = _('All Administrative Jurisdictions (Global)')

    # Dashboard metrics for this officer's scope
    total_count = complaints.count()
    pending_count = complaints.filter(status='PENDING').count()
    progress_count = complaints.filter(status='IN_PROGRESS').count()
    resolved_count = complaints.filter(status='RESOLVED').count()
    rejected_count = complaints.filter(status='REJECTED').count()

    # Apply filters (location, category, status)
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')

    if category_filter:
        complaints = complaints.filter(category=category_filter)
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if search_query:
        complaints = complaints.filter(
            Q(reference_number__icontains=search_query) | 
            Q(title__icontains=search_query) | 
            Q(citizen_name__icontains=search_query)
        )

    # Context variables
    categories = Complaint.CATEGORY_CHOICES
    statuses = Complaint.STATUS_CHOICES

    return render(request, 'dashboard_officer.html', {
        'complaints': complaints,
        'profile': profile,
        'scope_title': scope_title,
        'total_count': total_count,
        'pending_count': pending_count,
        'progress_count': progress_count,
        'resolved_count': resolved_count,
        'rejected_count': rejected_count,
        'categories': categories,
        'statuses': statuses,
        'selected_category': category_filter,
        'selected_status': status_filter,
        'search_query': search_query,
    })

@login_required
def admin_dashboard(request):
    # Verify user is Admin
    profile = get_object_or_404(OfficerProfile, user=request.user)
    if profile.role != 'ADMIN':
        messages.error(request, _('Access denied. You do not have administrator privileges.'))
        return redirect('officer_dashboard')

    # Global complaints list
    complaints = Complaint.objects.all()
    
    # Analytics metrics
    total_count = complaints.count()
    pending_count = complaints.filter(status='PENDING').count()
    progress_count = complaints.filter(status='IN_PROGRESS').count()
    resolved_count = complaints.filter(status='RESOLVED').count()
    
    # Group by category for Chart.js
    category_chart_data = complaints.values('category').annotate(count=Count('id'))
    category_labels = []
    category_counts = []
    category_dict = dict(Complaint.CATEGORY_CHOICES)
    for data in category_chart_data:
        category_labels.append(str(category_dict.get(data['category'], data['category'])))
        category_counts.append(data['count'])

    # Group by district for Chart.js
    district_chart_data = complaints.values('district__name').annotate(count=Count('id'))
    district_labels = []
    district_counts = []
    for data in district_chart_data:
        district_labels.append(str(data['district__name'] or _('Unknown')))
        district_counts.append(data['count'])

    # User management lists
    officers = OfficerProfile.objects.filter(role='OFFICER').select_related('user', 'assigned_district', 'assigned_pradeshiya_sabha', 'assigned_wasama')

    # Handle creation of locations (Districts, Sabhas, Wasamas) or new Officers in same page POST
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_officer':
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '').strip()
            district_id = request.POST.get('district', '')
            sabha_id = request.POST.get('sabha', '')
            wasama_id = request.POST.get('wasama', '')

            if username and password:
                if User.objects.filter(username=username).exists():
                    messages.error(request, _('Username "%(username)s" already exists.') % {'username': username})
                else:
                    new_user = User.objects.create_user(username=username, email=email, password=password)
                    profile = OfficerProfile.objects.create(
                        user=new_user,
                        role='OFFICER',
                        assigned_district_id=int(district_id) if district_id else None,
                        assigned_pradeshiya_sabha_id=int(sabha_id) if sabha_id else None,
                        assigned_wasama_id=int(wasama_id) if wasama_id else None
                    )
                    messages.success(request, _('Officer "%(username)s" created successfully!') % {'username': username})
            else:
                messages.error(request, _('Username and password are required.'))
            return redirect('admin_dashboard')

    districts = District.objects.all()
    return render(request, 'dashboard_admin.html', {
        'total_count': total_count,
        'pending_count': pending_count,
        'progress_count': progress_count,
        'resolved_count': resolved_count,
        'category_labels': category_labels,
        'category_counts': category_counts,
        'district_labels': district_labels,
        'district_counts': district_counts,
        'officers': officers,
        'districts': districts,
        'complaints': complaints[:10]  # Show recent 10 complaints in admin landing
    })

@login_required
def update_complaint_status(request, complaint_id):
    if request.method == 'POST':
        complaint = get_object_or_404(Complaint, id=complaint_id)
        
        # Check permissions: officer's assigned location must match the complaint location
        profile = get_object_or_404(OfficerProfile, user=request.user)
        
        # Admin can update anything. Officers are restricted to their boundaries:
        is_authorized = False
        if profile.role == 'ADMIN':
            is_authorized = True
        elif profile.assigned_wasama and complaint.wasama == profile.assigned_wasama:
            is_authorized = True
        elif profile.assigned_pradeshiya_sabha and complaint.pradeshiya_sabha == profile.assigned_pradeshiya_sabha:
            is_authorized = True
        elif profile.assigned_district and complaint.district == profile.assigned_district:
            is_authorized = True
        elif not profile.assigned_district and not profile.assigned_pradeshiya_sabha and not profile.assigned_wasama:
            # Global officer
            is_authorized = True

        if not is_authorized:
            messages.error(request, _('You are not authorized to update this complaint (outside your jurisdiction).'))
            return redirect('dashboard_router')

        status_to = request.POST.get('status')
        remark_text = request.POST.get('remark', '').strip()

        if status_to in dict(Complaint.STATUS_CHOICES):
            status_from = complaint.status
            complaint.status = status_to
            complaint.save()

            # Record history
            ComplaintRemark.objects.create(
                complaint=complaint,
                officer=request.user,
                remark=remark_text or _('Status updated to %(status)s.') % {'status': complaint.get_status_display()},
                status_from=status_from,
                status_to=status_to
            )
            messages.success(request, _('Complaint %(reference)s updated successfully!') % {'reference': complaint.reference_number})
        else:
            messages.error(request, _('Invalid status selected.'))
            
    return redirect('dashboard_router')
