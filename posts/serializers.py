from rest_framework import serializers

from .models import Category, Tag, BlogPost, Comment


class CategorySeriaizer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class BlogPostListSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source="author.email", read_only=True)
    category = CategorySeriaizer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = BlogPost
        fields = ("id", "title", "slug", "author_email", "category", "tags", "featured_image", "status", "created_at")


class BlogPostDetailSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    category = CategorySeriaizer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(many=True, write_only=True, queryset=Tag.objects.all(), source="tags")
    category_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Category.objects.all(),
                                                     source="category")


class Meta:
    model = BlogPost
    fields = (
        "id", "title", "slug", "content",
        "category", "category_id",
        "tags", "tag_ids",
        "featured_image", "status",
        "author", "created_at", "updated_at"
    )
    read_only_fields = ("slug", "create_at", "updated_at")

    def get_author(self, obj):
        return {"id": str(obj.author.id), "email": obj.author.email, "full_name": getattr(obj.author, "full_name", "")}

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        post = BlogPost.objects.create(**validated_data)
        if tags:
            post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


class CommentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "blog", "user", "user_email", "comment", "created_at")
        read_only_fields = ("user", "user_email", "created_at")
