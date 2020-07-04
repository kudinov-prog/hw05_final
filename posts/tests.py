from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import redirect, reverse
from django.test import TestCase, Client
from .models import Post, Group, User, Comment


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
        cache.clear()
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
            cache.clear()
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
            cache.clear()
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
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        self.post = Post.objects.create(author=self.user,
                                        text='text',
                                        group=self.group,
                                        image=uploaded)       
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
        """ Проверяет корректность загрузки изображения в форме.
        """
        txt = SimpleUploadedFile(
            name='small.txt',
            content=b'abc',
            content_type='text/plain'
        )
        response = self.client.post(reverse('post_edit',
                                    kwargs={'username': self.user.username,
                                            'post_id': self.post.id}), 
                                    data={'text': 'post with image',
                                          'image': txt})
        self.assertFormError(
            response,
            form='form',
            field='image',
            errors='Загрузите правильное изображение. Файл, который вы' +
            ' загрузили, поврежден или не является изображением.'
            )


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


class TestFollow(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username="my_user",
                                        password="12345")
        self.client.force_login(self.user)

    def test_auth_user_can_follow(self):
        """ Авторизованный пользователь может подписываться на других
            пользователей.
        """
        test_user = User.objects.create(username="follow", password="12345")

        self.client.get(reverse('profile_follow',
                                kwargs={'username': test_user.username}))
        count = self.user.follower.all().count()
        self.assertEqual(count, 1)

    def test_auth_user_can_unfollow(self):
        """ Авторизованный пользователь может отписываться от других
            пользователей.
        """
        test_user = User.objects.create(username="follow", password="12345")

        self.client.get(reverse('profile_unfollow',
                                kwargs={'username': test_user.username}))
        count = self.user.follower.all().count()
        self.assertEqual(count, 0)

    def test_check_post_in_index_follow(self):
        """ Новая запись пользователя появляется в ленте тех, кто на него
            подписан.
        """
        user_follower = User.objects.create(username="follow",
                                            password="12345")
        
        self.client.get(reverse('profile_follow',
                                kwargs={'username': user_follower.username}))
        post_user_follower = Post.objects.create(author=user_follower,
                                                 text='text_follower')
        response = self.client.get(reverse('follow_index'))
        self.assertContains(response, post_user_follower.text)

    def test_check_post_in_index_no_follow(self):
        """ Новая запись пользователя не появляется в ленте тех, кто на него
            не подписан.
        """
        user_no_follower = User.objects.create(username="no_follow",
                                               password="12345")
        post_user_no_follower = Post.objects.create(author=user_no_follower,
                                                    text='text_no_follower')
        response = self.client.get(reverse('follow_index'))
        self.assertNotContains(response, post_user_no_follower.text)

    def test_auth_user_can_comment(self):
        """ Проверяет создание авторизированным пользователем комментария
        """
        post = Post.objects.create(author=self.user, text='text_for_comment')
        self.client.post(
            reverse('add_comment', kwargs={'username': self.user.username,
                                           'post_id': post.id}),
            data={'text': 'test_text'}
            )
        comment = Comment.objects.first()
        self.assertEqual(comment.text, 'test_text')

    def test_not_auth_user_cant_comment(self):
        """ Проверяет невозможность создания коментария не авторизированным
            пользователем.
        """
        client_1 = Client()
        post = Post.objects.create(author=self.user, text='text_for_comment')
        
        client_1.post(
            reverse('add_comment', kwargs={'username': self.user.username,
                                           'post_id': post.id}),
            data={'text': 'test_text'}
            )
        comment= Comment.objects.first()
        self.assertEqual(comment, None)
