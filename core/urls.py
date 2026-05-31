from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    # Health checks
    path('health/live/', views.health_live, name='health_live'),
    path('health/ready/', views.health_ready, name='health_ready'),

    # Public pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('submit-contact/', views.submit_contact, name='submit_contact'),
    path('submit-chat-lead/', views.submit_chat_lead, name='submit_chat_lead'),
    path('partnerships/', views.partnerships, name='partnerships'),
    path('partnerships/lead/', views.submit_partner_lead, name='submit_partner_lead'),

    # Testimonials
    path('testimonial/<int:pk>/', views.testimonial_detail, name='testimonial_detail'),

    # Blog
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin/upload-video/', views.upload_video, name='upload_video'),

    # Golden Visa cards
    path('golden-visa/<slug:slug>/', views.golden_visa_card_detail, name='golden_visa_card_detail'),

    # Events
    path('events/', views.event_list, name='event_list'),
    path('events/<slug:slug>/', views.event_detail, name='event_detail'),

    # Landing pages
    path('greece-golden-visa/', views.greek_golden_visa, name='greece_golden_visa'),
    path('greecegoldenvisa/', views.greek_golden_visa, name='greek_golden_visa'),  # legacy
    path('fa/greece-golden-visa/', views.greece_golden_visa_fa_ads, name='greece_golden_visa_fa_ads'),

    # Persian /fa-new/ is handled by apps.persian_cms.urls (separate CMS/admin)

    # Webinar Landing (FA / UAE-Turkey audience)
    path('webinar/', views.webinar_landing, name='webinar_landing'),
    path('fa/UAEwebinar/', views.webinar_landing, name='webinar_landing_fa_ads'),
    path('webinar/register/', views.webinar_register, name='webinar_register'),

    # AI chat reply (OpenAI-powered concierge)
    path('chat/ai/', views.ai_chat_reply, name='ai_chat_reply'),

    # Live chat session
    path('chat/start/', views.chat_session_start, name='chat_session_start'),
    path('chat/notify/', views.chat_notify_agent, name='chat_notify_agent'),
    path('chat/message/', views.chat_user_message, name='chat_user_message'),
    path('chat/poll/', views.chat_poll, name='chat_poll'),

    # Agent chat
    path('agent/chat/', views.agent_chat_inbox, name='agent_chat_inbox'),
    path('agent/chat/<str:session_key>/', views.agent_chat_session, name='agent_chat_session'),
    path('agent/chat/<str:session_key>/takeover/', views.agent_takeover, name='agent_takeover'),
    path('agent/chat/<str:session_key>/send/', views.agent_send_message, name='agent_send_message'),
    path('agent/chat/<str:session_key>/close/', views.agent_close_session, name='agent_close_session'),
    path('agent/chat/<str:session_key>/poll/', views.agent_poll, name='agent_poll'),
]
