from django.contrib import admin
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Enrollment, Submission


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 3


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 2


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 3


class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    inlines = [QuestionInline]


class InstructorAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_learners', 'full_time']


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'lesson']
    inlines = [ChoiceInline]


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'question', 'is_correct']


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor, InstructorAdmin)
admin.site.register(Learner)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Enrollment)
admin.site.register(Submission)
