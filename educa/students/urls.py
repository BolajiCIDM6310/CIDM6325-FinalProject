from django.urls import path
from . import views
from django.views.decorators.cache import cache_page

urlpatterns = [
    path(
        'register/',
        views.StudentRegistrationView.as_view(),
        name='student_registration'
    ),
    path(
        'enroll-course/',
        views.StudentEnrollCourseView.as_view(),
        name='student_enroll_course'
    ),
    path(
        'courses/',
        views.StudentCourseListView.as_view(),
        name='student_course_list'
    ),
    path(
        'course/<pk>/',
        cache_page(60 * 1)(views.StudentCourseDetailView.as_view()),
        name='student_course_detail'
    ),
    path(
        'course/<pk>/<module_id>/',
        cache_page(60 * 1)(views.StudentCourseDetailView.as_view()),
        name='student_course_detail_module'
    ),
    path("mine_port/<int:course_id>", views.ManagePortListView.as_view(), name="manage_port_list"),
    path("create_port/<int:course_id>", views.PortCreateView.as_view(), name="port_create"),
    path("<int:course_id>/<int:pk>/edit_port/", views.PortUpdateView.as_view(), name="port_edit"),
    path("<int:course_id>/<pk>/delete_port/", views.PortDeleteView.as_view(), name="port_delete"),

    path(
        "portfolio/<int:port_id>/content/<model_name>/create/",
        views.PortContentCreateUpdateView.as_view(),
        name="portfolio_content_create",
    ),
    path(
        "portfolio/<int:port_id>/content/<model_name>/<id>/",
        views.PortContentCreateUpdateView.as_view(),
        name="portfolio_content_update",
    ),
    path(
        "content/<int:id>/delete/",
        views.PortContentDeleteView.as_view(),
        name="portfolio_content_delete",
    ),
    # path(
    #     "portfolio/<int:portfolio_id>/",
    #     views.PortfolioContentListView.as_view(),
    #     name="portfolio_content_list",
    # ),

    # path(
    #     "portfolio/<int:portfolio_id>/",
    #     views.PortfolioContentListView.as_view(),
    #     name="portfolio_content_list",
    # ),


    path(
        "portfolio/<int:portfolio_id>/li",
        views.PortfolioContentListView.as_view(),
        name="portfolio_content_list",
    ),
    
    # path(
    #     'portfolio/order/',
    #     views.PortContentOrderView.as_view(),
    #     name='port_content_order'
    # ),
]
