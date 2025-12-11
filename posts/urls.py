# posts/urls.py
from django.urls import path

from . import views

urlpatterns = [
    # categories
    path("categories/", views.CategoryListCreateAPIView.as_view(), name="categories-list-create"),
    path("categories/<uuid:pk>/", views.CategoryRUDAPIView.as_view(), name="category-detail"),

    # tags
    path("tags/", views.TagListCreateAPIView.as_view(), name="tags-list-create"),
    path("tags/<uuid:pk>/", views.TagRUDAPIView.as_view(), name="tag-detail"),

    # posts
    path("", views.PostListAPIView.as_view(), name="posts-list"),  # GET: list posts
    path("create/", views.PostCreateAPIView.as_view(), name="post-create"),  # POST: create post
    path("<uuid:pk>/", views.PostRetrieveUpdateDestroyAPIView.as_view(), name="post-detail"),  # GET/PUT/PATCH/DELETE

    # comments
    path("<uuid:post_id>/comments/", views.CommentListCreateAPIView.as_view(), name="comments-list-create"),
    path("comments/<uuid:pk>/", views.CommentRUDAPIView.as_view(), name="comment-detail"),
]
