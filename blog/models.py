from django.db import models


# Create your models here.

class Article(models.Model):
    ARTICLE_TYPE_CHOICES = [
        ("albinism", "albinism"),
        ("ZhangYuan", "ZhangYuan"),
        ("Chen Yuang", "Chen Yuang"),
        ("you", "you"),
        ("me", "me")
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32, default='Title')
    content = models.TextField(null=True)
    article_type = models.CharField(choices=ARTICLE_TYPE_CHOICES, max_length=40, verbose_name='文章种类')
    pub_time = models.DateTimeField(auto_now_add=True, verbose_name='发布时间', null=True)

    def __str__(self):
        return self.title


# class ChatSession(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True)
#     now_role = models.CharField(max_length=20, default='白', verbose_name='当前会话的角色', null=True)
#     chat_id = models.CharField(max_length=50, verbose_name='会话id', null=False, unique=True)
#     # 其他会话相关字段
#
#
# class ChatMessage(models.Model):
#     USER_CHOICES = (
#         ('白化', '白'),
#         ('邱', '邱'),
#         ('陈羽昂', '陈'),
#         ('你', '你'),
#         ('我', '我'),
#     )
#
#     ROLE_CHOICES = (
#         ("system", "system"),
#         ("assistant", "assistant"),
#         ("user", "user"),
#     )
#
#     session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES)
#     content = models.TextField()
#     user = models.CharField(max_length=20, choices=USER_CHOICES, verbose_name='角色', null=True)


class FantasyRecord(models.Model):
    title = models.CharField(max_length=32, verbose_name='标题', null=False)
    data = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    id = models.UUIDField(primary_key=True, editable=False)
    image = models.ImageField(upload_to='images', default='media/images/default.png', verbose_name='图片')


class FantasyMessage(models.Model):
    role = models.CharField(max_length=20, verbose_name='角色', null=False)
    message = models.TextField()
    record = models.ForeignKey(FantasyRecord, on_delete=models.CASCADE)
    time = models.DateTimeField(verbose_name='发布时间')
