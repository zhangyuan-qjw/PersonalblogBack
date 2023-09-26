from rest_framework import serializers
from .models import Article, FantasyMessage, FantasyRecord


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.article_type = validated_data.get('article_type', instance.article_type)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance

    def create(self, validated_data):
        Article.objects.create(**validated_data)
        return validated_data


# class ChatMessageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ChatMessage
#         fields = '__all__'
#
#     def create(self, validated_data):
#         chat_message = ChatMessage.objects.create(**validated_data)
#         return chat_message
#
#
# class ChatSessionSerializer(serializers.ModelSerializer):
#     messages = ChatMessageSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = ChatSession
#         fields = '__all__'
#         # extra_kwargs = {'messages': {'required': False}}
#
#     def create(self, validated_data):
#         chat_session = ChatSession.objects.create(**validated_data)
#         return chat_session


class FantasyMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FantasyMessage
        fields = '__all__'

    def create(self, validated_data):
        fantasy = FantasyMessage.objects.create(**validated_data)
        return fantasy


class FantasyRecordSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=True)
    image = serializers.ImageField(use_url=False)

    class Meta:
        model = FantasyRecord
        fields = '__all__'

    def create(self, validated_data):
        fantasy = FantasyRecord.objects.create(**validated_data)
        return fantasy
