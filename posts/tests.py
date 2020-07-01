from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.files.images import ImageFile
from django.shortcuts import redirect, reverse
from django.test import TestCase, Client
from .models import Post, Group, User


class TestPostsMethods(TestCase):

    def setUp(self): 
 
        self.client = Client() 
        self.user = User.objects.create_user(username='test_user', 
                                             password='12345') 
        self.group = Group.objects.create(title='group', slug='group') 
        self.client.force_login(self.user) 
 
    def test_profile_page_exist(self): 
        """ После регистрации пользователя создается его персональная  
            страница (profile) 
        """ 
        response = self.client.get("/test_user/") 
        self.assertEqual(response.context["user"].username, 
                         self.user.username) 
        self.assertEqual(response.status_code, 200) 
 
    def test_new_post(self): 
        """ Авторизованный пользователь может опубликовать пост (new) 
        """ 
        data = {'text': 'text', 'group': self.group.id} 
        self.client.post(reverse("new_post"), 
                         data=data, follow=True) 
        post = Post.objects.first() 
        response = self.client.get(reverse('index'), follow=True) 
        check_list = (post.text, post.group.id, post.author) 
 
        for item in check_list: 
            self.assertContains(response, item) 
        self.assertEqual(response.status_code, 200) 
         
    def test_unauthorized_user_post(self): 
        """ Неавторизованный посетитель не может опубликовать пост  
            (его редиректит на страницу входа) 
        """ 
 
        self.client.logout() 
 
        data = {'text': 'text', "group": self.group.id} 
        response = self.client.post(reverse("new_post"), 
                                    data=data, follow=True) 
        posts_count = Post.objects.all().count() 
 
        self.assertEqual(posts_count, 0) 
        self.assertRedirects(response, '/auth/login/?next=/new/') 
 
    def check_post(self, url, text, group, author): 
         
            response = self.client.get(url, follow=True) 
            paginator = response.context.get('paginator') 
             
            if paginator is not None: 
                post = response.context['page'][0] 
            else: 
                post = response.context['post'] 
                 
            self.assertEqual(post.text, text) 
            self.assertEqual(post.group, group) 
            self.assertEqual(post.author, author) 
 
    def test_new_post_on_all_page(self): 
        """ После публикации поста новая запись появляется на главной странице  
            сайта (index), на персональной странице пользователя (profile),  
            и на отдельной странице поста (post) 
        """ 
 
        new_post = Post.objects.create(author=self.user, text='text', 
                                       group=self.group, id='100') 
        urls = (reverse('index'), 
                reverse('profile', 
                        kwargs={'username': self.user.username}), 
                reverse('post', 
                        kwargs={'username': self.user.username, 
                                'post_id': new_post.id})) 
 
        for url in urls: 
            self.check_post( 
                url, 
                new_post.text, 
                new_post.group, 
                new_post.author 
            ) 
 
    def test_user_edit(self): 
        """ Авторизованный пользователь может отредактировать свой пост и  
            его содержимое изменится на всех связанных страницах 
        """ 
        new_post = Post.objects.create(author=self.user, text='text', 
                                       group=self.group, id='100') 
        new_group = Group.objects.create(title='new_group', slug='new_group') 
 
        self.client.post(reverse('post_edit', 
                                 kwargs={'username': self.user.username, 
                                         'post_id': new_post.id}), 
                                 data={'text': 'new_text', 
                                       'group': new_group.id}, 
                                 follow=True) 
 
        urls = (reverse('index'), 
                reverse('group_posts', 
                        kwargs={'slug': new_group.slug}), 
                reverse('profile', 
                        kwargs={'username': self.user.username}), 
                reverse('post', 
                        kwargs={'username': self.user.username, 
                                'post_id': new_post.id})) 
         
        for url in urls: 
            self.check_post(url, 'new_text', 
                                 new_group, 
                                 self.user)

    def test_code_404(self):
        """ Проверяет возвращает ли сервер код 404,
            если страница не найдена.
        """

        response = self.client.get("/test/")
        self.assertEqual(response.status_code, 404)


class TestPostsImages(TestCase):

    def setUp(self):

        self.client = Client()
        self.user = User.objects.create_user(username='user',
                                             password='12345')
        self.group = Group.objects.create(title='group', slug='group')   
        with open('media/posts/header-91.jpg','rb') as img:
            self.post = Post.objects.create(author=self.user,
                                            text='text',
                                            group=self.group,
                                            image=ImageFile(img,
                                                            'header-91.jpg'))       
        self.client.force_login(self.user)

    def test_check_post_img(self):
        """ Проверяет страницу конкретной записи с 
            картинкой: на странице есть тег <img>
        """
        url = reverse('post', kwargs={'username': self.user.username,
                                      'post_id': self.post.id})
        response = self.client.get(url, follow=True)
        self.assertContains(response, text='<img', status_code=200, count=1)

    def test_img_on_all_page(self):
        """ Проверяет, что на главной странице, на странице профайла и на
            странице группы пост с картинкой отображается корректно,
            с тегом <img>
        """
        urls = (reverse('index'),
                reverse('group_posts',
                        kwargs={'slug': self.group.slug}),
                reverse('profile',
                        kwargs={'username': self.user.username}))
        for url in urls:
            cache.clear()
            response = self.client.get(url, follow=True)
            self.assertContains(response, status_code=200, text='<img')

    def test_upload_image(self):
        with open('media/posts/test.txt','rb') as file:
            response = self.client.post(reverse('post_edit',
                                        kwargs={'username': self.user.username,
                                                'post_id': self.post.id}), 
                                        data={'text': 'post with image',
                                              'image': file})
        self.assertFormError(response,
                             form='form',
                             field='image',
                             errors='Загрузите правильное изображение. Файл, который вы загрузили, поврежден или не является изображением.')


class TestCache(TestCase):

    def setUp(self):
        self.client = Client()

    def test_check_cache(self):
        """ Проверяет кеширование списка постов на страниц index
        """
        self.client.get(reverse('index'))

        user = User.objects.create_user(username='user',
                                        password='12345')
        post = Post.objects.create(author=user,
                                   text='text_cache')

        response = self.client.get(reverse('index'))
        self.assertNotContains(response, post.text)

        key = make_template_fragment_key('index_page',
                                         [response.context['page'].number])
        cache.delete(key)

        response = self.client.get(reverse('index'))
        self.assertContains(response, post.text)
