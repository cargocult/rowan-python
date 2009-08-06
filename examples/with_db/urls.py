from rowan.core.controllers import Router
import controllers

master_urls = Router(
    ('^/$', controllers.view_blog),
    )