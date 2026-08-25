from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Count, Q, Value, IntegerField
from django.core.paginator import Paginator

from .models import Profile, EnrolledCourse, Course, SavedCourse
from .utils import check_field_values
from .forms import UserUpdateForm, ProfileUpdateForm


def home_view(request):
    return render(request, 'main_app/index.html')

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        is_instructor = request.POST.get("is_instructor")

        if False in check_field_values([username, firstname, lastname, password, password2]):
            messages.error(request, "All fields are required")
            return redirect("mainapp:signup", permanent=True)

        if User.objects.filter(username=username).exists():
            messages.info(request, "Username already taken")
            return redirect("mainapp:signup", permanent=True)
        
        if password != password2:
            messages.info(request, "Password does not match!")
            return redirect("mainapp:signup", permanent=True)
        
        user = User.objects.create_user(username=username, password=password, first_name=firstname, last_name=lastname)

        if is_instructor:
            profile = Profile.objects.create(user=user, is_instructor=True)
        else:
            profile = Profile.objects.create(user=user)
        messages.success(request, "Account created successfully.")
        return redirect("mainapp:login", permanent=True)

    # Return Sign up form for GET requests
    return render(request, 'main_app/signup.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if False in check_field_values([username, password]):
            messages.error(request, "All fields are required")
            return redirect("mainapp:login", permanent=True)

        user=authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("mainapp:courses")

        messages.error(request, "invalid username or password")
        return redirect("mainapp:login", permanent=True)

    return render(request, "main_app/login.html")

def logout_view(request):
    logout(request)
    return redirect("mainapp:login")



@never_cache
@login_required(login_url='mainapp:login')
def dashboard(request):
    if request.user.profile.is_instructor:
        return render(request, "main_app/instructor/dashboard.html")

    user = (
        User.objects.select_related('profile')
        .prefetch_related('profile__enrolled_courses__course')
        .annotate(
            enrolled_courses=Count('profile__enrolled_courses'),
            completed_courses=Count('profile__enrolled_courses', filter=Q(profile__enrolled_courses__is_completed=True)),
            ongoing_courses=Count('profile__enrolled_courses', filter=Q(profile__enrolled_courses__is_completed=False))
        )
        .get(id=request.user.id)
    )

    context = {
        'user':user
    }

    return render(request, "main_app/student/dashboard.html", context=context)


@never_cache
@login_required(login_url="mainapp:login")
def mycourses_view(request):
    queryset = EnrolledCourse.objects.filter(student__user_id=request.user.id).select_related('course')

    if request.method == "GET":
        return render(request, "main_app/student/mycourses.html", context={'enrolled_courses': queryset})
    
    elif request.method == "POST":
        enrolled_course_id = request.POST.get("enrolled_course_id")

        EnrolledCourse.objects.filter(id=enrolled_course_id, profile=request.user.profile).delete()
        messages.success(request, "Course Dropped successfully.")

        return render(request, "main_app/student/mycourses.html", context={'enrolled_courses': queryset})


@never_cache
@login_required(login_url="mainapp:login")
def settings_view(request):
    """
    Handles displaying the user's current info and updating their profile (First Name, Last Name, Email and Avatar) on form submission
    """

    if request.method == "POST":
        user_form = UserUpdateForm(
            request.POST,
            instance=request.user,
        )

        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile,
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            return redirect("mainapp:settings")

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }

    return render(
        request,
        "main_app/student/settings.html",
        context=context
    )


@login_required(login_url="mainapp:login")
def saved_courses_view(request):
    saved_courses = SavedCourse.objects.filter(student=request.user.profile).all()

    context = {
        'saved_courses':saved_courses
    }

    return render(request, "main_app/student/saved_courses.html", context=context)

@login_required(login_url="mainapp:login")
def courses_view(request):
    courses = Course.objects.filter(is_published=True).annotate(average_rating=Value(4, output_field=IntegerField()))

    # Get only matches if user searches
    if request.GET.get('q'):
        search_query = request.GET.get('q')
        courses = Course.objects.filter(title__icontains=search_query, is_published=True).annotate(average_rating=Value(4, output_field=IntegerField()))

    paginator = Paginator(courses, 9)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    context = {
        "courses": page,
    }

    return render(request, 'main_app/student/courses.html', context=context)

