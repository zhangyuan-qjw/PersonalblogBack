from django.db import models


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


class Philosophy(models.Model):
    author = models.CharField(max_length=32, verbose_name='作者', null=False)
    content = models.TextField(null=True)
