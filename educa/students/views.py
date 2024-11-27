from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.views.generic.edit import FormView
from .forms import CourseEnrollForm
from django.views.generic.list import ListView
from courses.models import Course
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from .models import Portfolio, PortContent
from django.views.generic.base import TemplateResponseMixin, View
from django.apps import apps
from django.forms.models import modelform_factory
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.db.models import Count
from .models import File, Image, Video, Text
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
import os



#register students
class StudentRegistrationView(CreateView):
    template_name = 'students/student/registration.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('student_course_list')

    def form_valid(self, form):
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(
            username=cd['username'], password=cd['password1']
        )
        login(self.request, user)
        return result

#enroll students
class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'student_course_detail', args=[self.course.id]
        )

#list of courses enrolled for
class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])


#details of the courses enrolled for
class StudentCourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        if 'module_id' in self.kwargs:
            # get current module
            context['module'] = course.modules.get(
                id=self.kwargs['module_id']
            )
        else:
            # get first module
            context['module'] = course.modules.all()[0]
        return context


# # Mixin for reuseability
class OwnerMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            student=self.request.user
        )  # only returns data belonging to the current user
    
    


# # reuseable form for create and update view
class OwnerEditMixin:
    def form_valid(self, form):
        form.instance.student = self.request.user
        return super().form_valid(form)


#.........................................................................................

# class OwnerPortMixin(OwnerMixin, LoginRequiredMixin):
#     model = Portfolio
#     fields = ["title", "slug", "overview"]  # Exclude course and student fields
#     success_url = reverse_lazy("manage_port_list")

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["course"] = get_object_or_404(Course, id=self.kwargs["course_id"])
#         return context

class OwnerPortMixin(OwnerMixin, LoginRequiredMixin):
    model = Portfolio
    fields = ["title", "slug", "overview"]  # Exclude course and student fields

    def get_success_url(self):
        return reverse_lazy("manage_port_list", kwargs={"course_id": self.kwargs["course_id"]})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = get_object_or_404(Course, id=self.kwargs["course_id"])
        # print(context.Course)
        return context
    
    

class OwnerPortEditMixin(OwnerPortMixin, OwnerEditMixin):
    template_name = "students/portfolio/form.html"

    def form_valid(self, form):
        form.instance.student = self.request.user
        form.instance.course = get_object_or_404(Course, id=self.kwargs["course_id"])
        return super().form_valid(form)

class ManagePortListView(OwnerPortMixin, ListView):
    template_name = "students/portfolio/list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(course__id=self.kwargs["course_id"])

class PortCreateView(OwnerPortEditMixin, CreateView):
    # def form_valid(self, form):
    #     # Ensure course_id is retrieved from kwargs
    #     course = get_object_or_404(Course, id=self.kwargs['course_id'])
    #     form.instance.course = course
    #     form.instance.student = self.request.user
    #     return super().form_valid(form)
    pass

class PortUpdateView(OwnerPortEditMixin, UpdateView):
    pass

class PortDeleteView(OwnerPortMixin, DeleteView):
    template_name = "students/portfolio/delete.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(course__id=self.kwargs["course_id"])

#.........................................................................................

# managing contents for modules
class PortContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = "students/content/form.html"

    def get_model(self, model_name):
        if model_name in ["text", "video", "image", "file"]:
            return apps.get_model(app_label="students", model_name=model_name)
        return None


    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(
            model, 
            exclude=["student", "order", "created", "updated"]
        )
        print(model)
        # Apply specific restrictions based on the model
        if model == File:
            form_field = Form.base_fields["file"]
            form_field.validators = [FileExtensionValidator(allowed_extensions=["pdf"])]
        elif model == Image:
            form_field = Form.base_fields["file"]
            form_field.validators = [FileExtensionValidator(allowed_extensions=["png"])]
        elif model == Video:
            form_field = Form.base_fields["file"]
            form_field.validators = [FileExtensionValidator(allowed_extensions=["mp4"])]

        return Form(*args, **kwargs)

    def dispatch(self, request, port_id, model_name, id=None):
        self.portfolio = get_object_or_404(
            Portfolio, id=port_id, student=request.user
        )
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id, student=request.user)
        return super().dispatch(request, port_id, model_name, id)

    def get(self, request, port_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({"form": form, "object": self.obj})
    

    def post(self, request, port_id, model_name, id=None):
        form = self.get_form(
            self.model, instance=self.obj, data=request.POST, files=request.FILES
        )
        if form.is_valid():
            obj = form.save(commit=False)
            obj.student = request.user
            try:
                obj.clean()  # Run model-level validations
                obj.save()
                if not id:
                    PortContent.objects.create(portfolio=self.portfolio, item=obj)
                return redirect("portfolio_content_list", self.portfolio.id)
            except ValidationError as e:
                form.add_error(None, e)  # Add error to the form
        return self.render_to_response({"form": form, "object": self.obj})


# deleting contents
class PortContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(PortContent, id=id, portfolio__student=request.user)
        portfolio = content.portfolio
        content.item.delete()
        content.delete()
        return redirect("portfolio_content_list", portfolio.id)


class PortfolioContentListView(TemplateResponseMixin, View):
    template_name = "students/content/content_list.html"

    def get(self, request, portfolio_id):
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, student=request.user)
        portfolios = portfolio.course.stud_modules.filter(student = request.user)
        return self.render_to_response({"portfolio": portfolio, "portfolio_courses" : portfolios})
