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


# 白化博客接口
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


# 创建分页器
class ArticlePagination(PageNumberPagination):
    page_size = 10  # 默认每页显示的数据条数
    page_size_query_param = 'page_size'  # 前端传递的每页显示的数据条数的参数
    max_page_size = 20  # 每页最大显示的数据条数
    page_query_param = 'page'  # 前端传递的页码数的参数


# class TalkAIView(ViewSet):
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.session = None
#         self.message = ''
#         self.role = ''
#
#     @action(methods=['post'], detail=False, url_path='save')
#     def save_mysql(self, request):
#         session = request.data.get('session')
#         now_role = request.data.get('role')
#         session_data = {'chat_id': session, 'now_role': now_role}
#         chat_session_serializer = ChatSessionSerializer(data=session_data)
#         if chat_session_serializer.is_valid(raise_exception=True):
#             chat_session_serializer.save()
#         chat_session = ChatSession.objects.get(chat_id=session)
#         session_id = chat_session.id
#         messages = json.loads(cache.get(session))
#         for message in messages:
#             message['session'] = session_id
#         # 删除缓存
#         cache.delete(session)
#         cache.delete(f'{session}_role')
#         session_list = cache.get("sessions_list")
#         # 删除session_list中的session=0的数据
#         session_list = [d for d in session_list if d['chat_id'] != f'{session}']
#         cache.set('sessions_list', session_list, timeout=60 * 60)
#         message_serializer = ChatMessageSerializer(data=messages, many=True)
#         if message_serializer.is_valid(raise_exception=True):
#             message_serializer.save()
#             return Response({'code': 200, 'data': 'success'})
#         return Response({'code': 404, 'data': 'fail'})
#
#     @action(methods=['get'], detail=False, url_path='sessions')
#     def get_all_session(self, request):
#         # 查询所有的会话历史
#         histories = ChatSession.objects.all()
#         histories = ChatSessionSerializer(histories, many=True).data
#         cache_histories = cache.get('sessions_list')
#         if cache_histories:
#             histories += cache_histories
#         return Response({'code': 200, 'data': histories})
#
#     @action(methods=['get'], detail=False, url_path='messages')
#     def get_chat_history(self, request):
#         # 获取聊天记录
#         session = request.query_params.get('session')
#         sessionRole = f'{session}_role'
#         chat_history = cache.get(session)
#         if chat_history:
#             chat_history = json.loads(chat_history)
#             chat_history = [d for d in chat_history if d['role'] != 'system']
#             nowRole = cache.get(sessionRole)
#         else:
#             # 从MySQL数据库中获取
#             print('从MySQL数据库中获取')
#             nowRole = ChatSession.objects.get(chat_id=session).now_role
#             chat_history = self.get_mysql_history(session)
#             # 关联删除中的数据
#             ChatSession.objects.get(chat_id=session).delete()
#             # 将聊天记录存入redis
#             cache.set(sessionRole, nowRole)
#             cache.set(session, json.dumps(chat_history))
#             session_list = cache.get("sessions_list")
#             session_list.append({"chat_id": f'{session}', "created_at": time.time()})
#             cache.set("sessions_list", session_list, timeout=60 * 60)
#             chat_history = [d for d in chat_history if d['role'] != 'system']
#         return Response(
#             {'code': 200, 'data': {"role": nowRole, "session": f'{session}', "messages": chat_history}})
#
#     @action(methods=['post'], detail=False, url_path='talk')
#     def talk(self, request):
#         # 获取前端传递的参数
#         self.role = request.data.get('role')  # 角色
#         self.message = request.data.get('message')  # 消息
#         self.session = request.data.get('session')  # 会话
#         sessionRole = f'{self.session}_role'
#         if self.session is None:
#             # 创建一个hash表，并以当前时间戳为表名
#             self.session = int(time.time())
#             sessionRole = f'{self.session}_role'
#             cache.set(self.session, '[]', timeout=60 * 60)
#             cache.set(sessionRole, '', timeout=60 * 60)
#             # 判断session表是否存在
#             if cache.get("sessions_list"):
#                 session_list = cache.get("sessions_list")
#                 session_list.append({"chat_id": f'{self.session}', "created_at": time.time()})
#                 cache.set("sessions_list", session_list, timeout=60 * 60)
#             else:
#                 cache.set("sessions_list", [{"chat_id": f'{self.session}', "created_at": time.time()}], timeout=60 * 60)
#         sessionRole_old = cache.get(sessionRole)
#         if sessionRole_old == self.role:
#             isChange = False
#         else:
#             isChange = True
#             cache.set(sessionRole, self.role, timeout=60 * 60)
#         if isChange:
#             response = self.get_messages(True)
#         else:
#             response = self.get_messages(False)
#         return Response({'code': 200, 'data': {"role": self.role, "session": self.session, "content": response}})
#
#     def get_messages(self, is_new_role):
#         if is_new_role:
#             user_data = [{"role": "system",
#                           "content": f"（如果在前面的聊天中你是其他身份，请把之前你与用户的对话当成其他人与之的对话，并记住他们的聊天内容，如果前面没有聊天记录，请忽略。）从现在起，你的名字叫{self.role}（你必须伪装成他，并不被询问者发现），你是一个{self.get_role()}的人"},
#                          {"role": "user", "content": self.message, "user": "邱"}, ]
#         else:
#             user_data = [{"role": "user", "content": self.message, "user": "邱"}]
#         messages = cache.get(self.session)
#         if messages is None:
#             # 从mysql中获取会话，并再次缓存进redis
#             print('从mysql中获取会话')
#             pass
#         else:
#             # 从缓存中获取会话
#             messages = json.loads(messages)
#             messages += user_data
#             talk_messages = [{k: v for k, v in d.items() if k != 'user'} for d in messages]
#             response = talk(talk_messages)
#             # time.sleep(5)
#             # response = '万一考不上呢？如何考，怎么考？如何努力？白化，都是问题。况且，真的有必要考研吗？'
#             session_data = [{"role": "assistant", "content": response, "user": self.role}]
#             # 将会话和消息存入缓存
#             messages += session_data
#             cache.set(self.session, json.dumps(messages, ensure_ascii=False).encode('utf-8'), timeout=60 * 60)
#         return response
#
#     def get_role(self):
#         if self.role == '白化':
#             return '乐观'
#         elif self.role == '陈羽昂':
#             return '悲观'
#
#     @staticmethod
#     def get_mysql_history(session):
#         try:
#             # 查询session会话时链表查询messages
#             session_history = ChatSession.objects.prefetch_related('chatmessage_set').get(chat_id=session)
#             history = session_history.chatmessage_set.all()
#             history = ChatMessageSerializer(history, many=True).data
#         except ObjectDoesNotExist:
#             return []
#         return history

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
            print(data)
            one_messages = FantasyRecord.objects.get(id=uuid_id)
            print(one_messages)
            if image != 'undefined':
                record_data = {'image': image, 'title': data.get('title')}
                image_path = one_messages.image.path
                os.remove(image_path)
            else:
                record_data = {'title': data.get('title')}
                print(record_data)
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


class FantasyPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 10
