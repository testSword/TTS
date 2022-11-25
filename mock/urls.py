from django.contrib import admin

from django.urls import path, re_path

from mock.views import select_mock_interface, add_mock_interface, mock_tts

urlpatterns = [
    path("select_interface",select_mock_interface),
    path("add_interface", add_mock_interface),
    path("update_interface", select_mock_interface),
    path("delete_interface", select_mock_interface),
    path("add_mockdata", select_mock_interface),
    path("edit_mockdata", select_mock_interface),
    path("delete_mockdata", select_mock_interface),
    path("shuffle_mockdata", select_mock_interface),
    path("confirm_mockdata", select_mock_interface),
    path("mock_tts", mock_tts,)
]
