from django.http import HttpResponseRedirect
from .models import Course, Enrollment, Submission
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


def submit(request, course_id):
    course = Course.objects.get(id=course_id)
    enrollment = Enrollment.objects.get(user=request.user, course=course)
    submitted_answers = extract_answers(request)
    submission = Submission.objects.create(enrollment=enrollment)
    submission.choices.set(submitted_answers)
    submission.save()
    return HttpResponseRedirect(reverse(viewname='onlinecourse:show_exam_result', args=(course_id, submission.id)))


def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice-'):
            choice_id = int(key[7:])
            submitted_answers.append(choice_id)
    return submitted_answers


def show_exam_result(request, course_id, submission_id):
    course = Course.objects.get(id=course_id)
    submission = Submission.objects.get(id=submission_id)
    submission_choices = submission.choices.all()
    correct_choices = []
    correct, wrong = 0, 0

    for lesson in course.lesson_set.all():
        for question in lesson.question_set.all():
            for choice in question.choice_set.all():
                if choice.is_correct:
                    correct_choices.append(choice)

    for choice in submission_choices:
        if choice.is_correct:
            correct += 1
        else:
            wrong += 1

    for choice in correct_choices:
        if choice not in submission_choices:
            wrong += 1

    total = 0
    if correct + wrong == 0:
        total = 1
    else:
        total = correct + wrong

    grade = int(correct / total * 100)
    context = {'course': course, 'selected_choices': submission_choices, 'grade': grade}
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
