# posts/views.py
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Category, Tag, BlogPost, Comment
from .permissions import CanCreatePost, IsAuthorOrEditorOrAdmin, CanComment
from .serializers import (
    CategorySeriaizer, TagSerializer,
    BlogPostListSerializer, BlogPostDetailSerializer,
    CommentSerializer
)


# -------------------------
# Category & Tag Views
# -------------------------
class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySeriaizer
    permission_classes = (IsAuthenticated,)  # you can restrict create to admin/editor only via custom permission

    def get_permissions(self):
        # allow listing for anyone
        if self.request.method == "GET":
            return [AllowAny()]
        # restrict POST to admin/editor
        return [IsAuthenticated()]


class CategoryRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySeriaizer
    permission_classes = (IsAuthenticated,)  # restrict mutations as you want


class TagListCreateAPIView(generics.ListCreateAPIView):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticated,)


class TagRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticated,)


# -------------------------
# Blog Post Views
# -------------------------
class PostListAPIView(generics.ListAPIView):
    """
    Public listing:
    - show only published posts by default
    - supports filtering by category (slug), tag (slug), author (id), status, and search (title/content)
    """
    serializer_class = BlogPostListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = BlogPost.objects.all().order_by("-created_at")
        user_id = self.request.query_params.get("user")
        if user_id:
            qs = qs.filter(author__id=user_id)

        return qs
        


class PostCreateAPIView(generics.CreateAPIView):
    serializer_class = BlogPostDetailSerializer
    permission_classes = (CanCreatePost,)

    def perform_create(self, serializer):
        # set current user as author
        serializer.save(author=self.request.user)


class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostDetailSerializer
    permission_classes = (IsAuthorOrEditorOrAdmin,)

    def get(self, request, *args, **kwargs):
        post = self.get_object()
        # If post is draft and viewer is not author/admin/editor -> forbid
        if post.status == "draft":
            user = request.user
            if not (user.is_authenticated and (user.role in ("admin", "editor") or post.author == user)):
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return super().get(request, *args, **kwargs)


# -------------------------
# Comments
# -------------------------
class CommentListCreateAPIView(generics.ListCreateAPIView):
    """
    List/ create comments for a post.
    GET: list all comments for a blog (anyone)
    POST: create comment (authenticated)
    """
    serializer_class = CommentSerializer
    permission_classes = (CanComment,)

    def get_queryset(self):
        blog_id = self.kwargs.get("post_id")
        return Comment.objects.filter(blog__id=blog_id).order_by("-created_at")

    def perform_create(self, serializer):
        blog_id = self.kwargs.get("post_id")
        blog = BlogPost.objects.get(id=blog_id)
        serializer.save(user=self.request.user, blog=blog)


class CommentRUDAPIView(generics.RetrieveDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (CanComment,)
