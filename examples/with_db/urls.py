from rowan.core.controllers import Router
import views

master_urls = Router(
    ('^/$', views.view_blog),
    )