from django.contrib import admin

from django.urls import path, re_path

from mock.views import select_mock_interface, add_mock_interface, mock_tts, update_mock_interface, \
    delete_mock_interface, add_mock_data, edit_mock_data, delete_mock_data, shuffle_mock_data, confirm_mock_data, \
    select_mock_data

urlpatterns = [
    path("select_interface/",select_mock_interface),
    path("add_interface/", add_mock_interface),
    path("update_interface/", update_mock_interface),
    path("delete_interface/", delete_mock_interface),
    path("select_mockdata/", select_mock_data),
    path("add_mockdata/", add_mock_data),
    path("edit_mockdata/", edit_mock_data),
    path("delete_mockdata/", delete_mock_data),
    path("shuffle_mockdata/", shuffle_mock_data),
    path("confirm_mockdata/", confirm_mock_data),
    path("mock_tts", mock_tts,)
]
