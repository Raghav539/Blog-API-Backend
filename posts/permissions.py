# posts/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS


class CanCreatePost(BasePermission):
    """
    Allow create only for admin/editor/author.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ("admin", "editor", "author")


class IsAuthorOrEditorOrAdmin(BasePermission):
    """
    Allow update/delete if:
     - user.role in ("admin","editor") -> allowed
     - OR user is author of object -> allowed
    """

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS (GET) allowed
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.role in ("admin", "editor"):
            return True
        # allow author to edit/delete their own post
        return obj.author == user


class CanComment(BasePermission):
    """
    Only authenticated users can create comments; read allowed for all.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # delete/comment-specific: author of comment or admin/editor
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if user.role in ("admin", "editor"):
            return True
        return obj.user == user
