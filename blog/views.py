from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializer import ArticleSerializer, FantasyMessageSerializer, FantasyRecordSerializer
from rest_framework.pagination import PageNumberPagination
from .models import Article, FantasyRecord, FantasyMessage
import json
import uuid
import os


# 白化接口
class BlogView(GenericViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    @action(methods=['get'], detail=False, url_path='articles')
    def getListArticles(self, request):
        # 根据文章的种类获取文章
        article_type = request.query_params.get('article_type')
        queryset = self.get_queryset()

        if article_type:
            paginator = ArticlePagination()
            articles = queryset.filter(article_type=article_type).order_by('-pub_time')
            try:
                queryset = paginator.paginate_queryset(articles, request)
            except Exception as e:
                return Response({'code': 400, 'data': 'fail'})

        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})

    @action(methods=['post'], detail=False, url_path='addArticle')
    def addArticle(self, request):
        article_data = request.data
        # 添加文章
        articleSerializer = self.get_serializer(data=article_data)
        if articleSerializer.is_valid(raise_exception=True):
            articleSerializer.save()
            return Response({'code': 200, 'data': 'success'})
        else:
            return Response({'code': 400, 'data': 'fail'})

    @action(methods=['delete'], detail=False, url_path='deleteArticle')
    def deleteArticle(self, request):
        # 根据文章的id删除文章
        article_id = request.query_params.get('id')
        Article.objects.filter(id=article_id).delete()
        return Response({'code': 200, 'data': 'success'})

    # 修改文章
    @action(methods=['put'], detail=False, url_path='updateArticle')
    def updateArticle(self, request):
        article_data = request.data
        article_id = article_data.get('id')
        article = Article.objects.get(id=article_id)
        articleSerializer = self.get_serializer(article, data=article_data)
        if articleSerializer.is_valid(raise_exception=True):
            articleSerializer.save()
            return Response({'code': 200, 'data': 'success'})
        else:
            return Response({'code': 400, 'data': 'fail'})


class ArticlePagination(PageNumberPagination):
    page_size = 10  # 默认每页显示的数据条数
    page_size_query_param = 'page_size'  # 前端传递的每页显示的数据条数的参数
    max_page_size = 20  # 每页最大显示的数据条数
    page_query_param = 'page'  # 前端传递的页码数的参数


# 幻想日记接口
class FantasyView(ViewSet):

    @action(methods=['post'], detail=False, url_path='fantasy', url_name='fantasy')
    def save_messages(self, request):
        data = request.data
        id = data.get('id')
        if not id:
            uuid_id = uuid.uuid4()
            record_data = {'title': data.get('title'), 'id': uuid_id, 'image': data.get('image')}
            RecordSerializer = FantasyRecordSerializer(data=record_data)
            if RecordSerializer.is_valid(raise_exception=True):
                RecordSerializer.save()
        else:
            id = id.strip('"')
            uuid_id = uuid.UUID(id)
            image = data.get('image')
            one_messages = FantasyRecord.objects.get(id=uuid_id)
            if image != 'undefined':
                record_data = {'image': image, 'title': data.get('title')}
                image_path = one_messages.image.path
                os.remove(image_path)
            else:
                record_data = {'title': data.get('title')}
            RecordSerializer = FantasyRecordSerializer(one_messages, data=record_data, partial=True)
            if RecordSerializer.is_valid(raise_exception=True):
                RecordSerializer.update(one_messages, RecordSerializer.validated_data)
        messages = json.loads(data.get('messages'))
        new_messages = [{**d, 'record': uuid_id} for d in messages]
        MessageSerializer = FantasyMessageSerializer(data=new_messages, many=True)
        if MessageSerializer.is_valid(raise_exception=True):
            MessageSerializer.save()
        return Response({"code": 200, "msg": "保存成功"})

    @action(methods=['get'], detail=False, url_path='record')
    def get_record(self, request):
        FantasyRecord_data = FantasyRecord.objects.all().order_by("-data")
        FantasyRecord_serializer = FantasyRecordSerializer(FantasyRecord_data, many=True)
        return Response({"code": 200, "msg": "获取成功", "data": FantasyRecord_serializer.data})

    @action(methods=['get'], detail=False, url_path='information')
    def get_message(self, request):
        id = request.query_params.get('id')
        if not id:
            return Response({"code": 400, "msg": "缺少参数"})
        try:
            Fantasy_information = FantasyRecord.objects.prefetch_related('fantasymessage_set').get(id=id)
            Fantasy_information_data = Fantasy_information.fantasymessage_set.all()
            Fantasy_information_serializer = FantasyMessageSerializer(Fantasy_information_data, many=True)
            return Response({"code": 200, "msg": "获取成功", "data": Fantasy_information_serializer.data})
        except FantasyRecord.DoesNotExist:
            return Response({"code": 400, "msg": "获取失败"})

    @action(methods=['get'], detail=False, url_path='all_record')
    def get_all_recordMessages(self, request):
        # 获取所有FantasyRecord以及其惯量数据
        records = FantasyRecord.objects.all().order_by("-data")
        paginator = FantasyPagination()
        try:
            page = paginator.paginate_queryset(records, request)
        except:
            return Response({"code": 404, "msg": "已经是最后一页"})
        serializer = FantasyRecordSerializer(page, many=True)
        for record in serializer.data:
            messages = FantasyMessage.objects.filter(record=record['id'])
            message_serializer = FantasyMessageSerializer(messages, many=True)
            record['messages'] = message_serializer.data
        return Response({"code": 200, "msg": "获取成功", "data": serializer.data})

    @action(methods=['delete'], detail=False, url_path='delete_fantasy')
    def delete_fantasy(self, request):
        id = request.query_params.get('id')
        if not id:
            return Response({"code": 400, "msg": "缺少参数"})
        try:
            Fantasy_information = FantasyRecord.objects.prefetch_related('fantasymessage_set').get(id=id)
            # 先删除所有相关的 FantasyMessage
            Fantasy_information.fantasymessage_set.all().delete()
            # 再删除 FantasyRecord
            Fantasy_information.delete()
            return Response({"code": 200, "msg": "删除成功"})
        except FantasyRecord.DoesNotExist:
            return Response({"code": 400, "msg": "删除失败"})

    @action(methods=['get'], detail=False, url_path='random_images')
    def random_images(self, request):  # 随机获取图片
        images = FantasyRecord.objects.all().order_by('?')[:9]
        serializer = FantasyRecordSerializer(images, many=True)
        return Response({"code": 200, "msg": "获取成功", "data": serializer.data})


class FantasyPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 10

# 幻想图片接口
