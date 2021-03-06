from unittest import mock
from django.urls import reverse
from rest_framework import status
from authors.apps.articles.models import  Article

from authors.apps.articles.models import Article
from authors.apps.authentication.tests import (
    test_base, test_data
)
from authors.apps.articles.tests.test_data import (
    article_data, 
    test_user_data, 
    test_user2_data, 
    changed_article_data,
    article_data_no_body,
    like_data, dislike_data,
    user1_rating, user2_rating_fail,
    comment_1, comment_2, comment_3,
    search_article_data,
    search_article_data,
    user1_rating, user2_rating_fail,
    register_user1_data,
    register_user2_data,
    article_data1
    )
from rest_framework import status
from rest_framework.test import APITestCase
from authors.apps.articles.models import Article

class TestArticle(test_base.BaseTestCase):

    def test_get_article_not_authenticated(self):
        user_token = self.create_user(test_data.test_user_data)
        resp = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user_token, format='json')
        response = self.client.get('/api/articles/', format='json')
        title = response.data.get('results')[0].get('title')
        descr = response.data.get('results')[0].get('description')
        body = response.data.get('results')[0].get('body')
        self.assertEqual(title, article_data.get("title"))
        self.assertEqual(descr, article_data.get("description"))
        self.assertEqual(body, article_data.get("body"))

    def test_create_article(self):
        user_token = self.create_user(test_data.test_user_data)
        resp = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user_token, format='json')
        self.assertEqual(resp.data["article"]["title"], article_data.get("title"))
        self.assertEqual(resp.data["article"]["description"], article_data.get("description"))
        self.assertEqual(resp.data["article"]["body"], article_data.get("body"))
        self.assertEqual(resp.data["article"]["slug"], "hello-slug-first")
        self.assertEqual(resp.data["article"]["author"]["username"], "testuser")

    def test_get_article_authenticated(self):
        user_tkn = self.create_user(test_data.test_user_data)
        resp = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user_tkn, format='json')
        response = self.client.get('/api/articles/', HTTP_AUTHORIZATION=user_tkn, format='json')
        title = response.data.get('results')[0].get('title')
        body = response.data.get('results')[0].get('body')
        descr = response.data.get('results')[0].get('description')
        self.assertEqual(title, article_data.get("title"))
        self.assertEqual(descr, article_data.get("description"))
        self.assertEqual(body, article_data.get("body"))

    def test_get_article_by_id(self):
        user1_token = self.create_user(test_user_data)
        self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user1_token, format='json')
        self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user1_token, format='json')

        all_articles = self.client.get('/api/articles/', HTTP_AUTHORIZATION=user1_token, format='json')
        slug = all_articles.data.get('results')[0].get('slug')

        response = self.client.get(f'/api/articles/{slug}', HTTP_AUTHORIZATION=user1_token, format='json')

        self.assertEqual(response.data["title"], article_data["title"])
        self.assertEqual(response.data["description"], article_data.get("description"))
        self.assertEqual(response.data["body"], article_data.get("body"))

    def test_create_article_no_body(self):
        user_token = self.create_user(test_data.test_user_data)
        resp = self.client.post('/api/articles/', article_data_no_body, HTTP_AUTHORIZATION=user_token, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_owner_can_edit(self):
        user1_token = self.create_user(test_user_data)
        user2_token = self.create_user(test_user2_data)
        response = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user1_token, format='json')
        resp = self.client.put(f'/api/articles/{response.data["article"]["slug"]}', article_data, HTTP_AUTHORIZATION=user2_token, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_str_model(self):
        mock_instance = mock.Mock(spec=Article)
        mock_instance.title = "hello slug"
        mock_instance.description = "Short description about slug"
        self.assertEqual(Article.__str__(mock_instance), "hello slug")
        
    def test_like_an_article(self):
        user1_token = self.create_user(test_user_data)
        response = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user1_token, format='json')
        liked_article_id = response.data["article"]["slug"]
        user1_like_resp = self.client.post(f'/api/articles/{liked_article_id}/like', like_data,
                                            HTTP_AUTHORIZATION=user1_token, format='json')
        self.assertEqual(like_data["likes"], user1_like_resp.data["details"]["likes"])
        user1_like_again = self.client.post(f'/api/articles/{liked_article_id}/like', like_data,
                                            HTTP_AUTHORIZATION=user1_token, format='json')
        self.assertEqual({'msg': 'You have already liked this article'}, user1_like_again.data)  

    def test_dislike_an_article(self):
        user1_token = self.create_user(test_user_data) 
        response = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user1_token, format='json')
        user1_dislike_resp = self.client.post(f'/api/articles/{response.data["article"]["slug"]}/like', dislike_data,
                                            HTTP_AUTHORIZATION=user1_token, format='json') 
        self.assertEqual(dislike_data["likes"], user1_dislike_resp.data["details"]["likes"])
        user1_dislike_again = self.client.post(f'/api/articles/{response.data["article"]["slug"]}/like', dislike_data,
                                            HTTP_AUTHORIZATION=user1_token, format='json')   
        self.assertEqual({'msg': 'You have already disliked this article'}, user1_dislike_again.data)    

    def test_another_user_can_like(self):
        user1_token = self.create_user(test_user_data)
        user2_token = self.create_user(test_user2_data)
        response = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user1_token, format='json')
        user1_like_resp = self.client.post(f'/api/articles/{response.data["article"]["slug"]}/like', like_data,
                                            HTTP_AUTHORIZATION=user1_token, format='json')
        user2_like_resp = self.client.post(f'/api/articles/{response.data["article"]["slug"]}/like', like_data,
                                            HTTP_AUTHORIZATION=user2_token, format='json')
        get_articles = self.client.get('/api/articles/')
        self.assertEqual(2, get_articles.data["results"][0]["likes"])

    def test_like_then_dislike(self):
        user1_token = self.create_user(test_user_data)
        response = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user1_token, format='json')
        user1_like_resp = self.client.post(f'/api/articles/{response.data["article"]["slug"]}/like', like_data,
                                            HTTP_AUTHORIZATION=user1_token, format='json')
        user1_dislike_resp = self.client.post(f'/api/articles/{response.data["article"]["slug"]}/like', dislike_data,
                                            HTTP_AUTHORIZATION=user1_token, format='json')
        self.assertEqual(dislike_data["likes"], user1_dislike_resp.data["details"]["likes"]) 

    def test_favorite_article(self):
        user_token = self.create_user(test_data.test_user_data)
        response = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user_token, format='json')
        article_slug = response.data['article']['slug']
        response1 = self.client.post(f'/api/articles/{article_slug}/favorite', {'favorite': True}, HTTP_AUTHORIZATION=user_token, format='json')
        response2 = self.client.post(f'/api/articles/{article_slug}/favorite', {'favorite': True}, HTTP_AUTHORIZATION=user_token, format='json')
        response3 = self.client.post(f'/api/articles/{article_slug}/favorite', {'favorite': False}, HTTP_AUTHORIZATION=user_token, format='json')
        response4 = self.client.post(f'/api/articles/{article_slug}/favorite', {'favorite': False}, HTTP_AUTHORIZATION=user_token, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response3.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response4.status_code, status.HTTP_400_BAD_REQUEST)

    def test_favorite_list(self):
        user_token = self.create_user(test_data.test_user_data)
        response = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user_token, format='json')
        article_slug = response.data['article']['slug']
        response1 = self.client.post(f'/api/articles/{article_slug}/favorite', None, HTTP_AUTHORIZATION=user_token, format='json')
        response2 = self.client.get(f'/api/users/articles/favorites', HTTP_AUTHORIZATION=user_token, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def test_read_stats(self):
        user_token = self.create_user(test_data.test_user_data)
        response2 = self.client.get(f'/api/users/articles/most-recent-reads', HTTP_AUTHORIZATION=user_token, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def test_article_contains_share_links(self):
        """
        Test article contains share links
        """
        user_token = self.create_user(test_data.test_user_data)
        resp = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user_token, format='json')
        response = self.client.get('/api/articles/', format='json')
        self.assertEqual(response.data["results"][0]["share_article_links"]["facebook"], 
        'https://www.facebook.com/sharer/sharer.php?u=http%3A//testserver/api/articles/hello-slug-first')
        self.assertEqual(response.data["results"][0]["share_article_links"]["twitter"], 
        'https://twitter.com/home?status=http%3A//testserver/api/articles/hello-slug-first')
        self.assertEqual(response.data["results"][0]["share_article_links"]["googleplus"], 
        'https://plus.google.com/share?url=http%3A//testserver/api/articles/hello-slug-first')
        self.assertEqual(response.data["results"][0]["share_article_links"]["email"], 
        'mailto:?&subject=hello%20slug&body=hello%20slug%0A%0Ahttp%3A//testserver/api/articles/hello-slug-first')
        
    def test_user_can_rate_article(self):
        user_token = self.create_user(test_user_data)
        resp = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user_token, format='json')
        self.assertEqual(resp.data['article']['average_rating'], None)

        article_slug = resp.data['article']['slug']
        fail_response = self.client.post(f'/api/articles/{article_slug}/rate', user2_rating_fail, HTTP_AUTHORIZATION=user_token, format='json')
        self.assertIn('Ratings should be between 0-5', fail_response.data['errors']['ratings'])

        
        response = self.client.post(f'/api/articles/{article_slug}/rate', user1_rating, HTTP_AUTHORIZATION=user_token, format='json')
        self.assertEqual(response.data['message'], 'Rating received')

        rate_again = self.client.post(f'/api/articles/{article_slug}/rate', user1_rating, HTTP_AUTHORIZATION=user_token, format='json')
        self.assertEqual(rate_again.data['message'], 'You have already rated.')


    def test_author_search(self):
        user_token = self.create_user(test_user_data)
        self.client.post('/api/articles/', search_article_data, HTTP_AUTHORIZATION=user_token, format='json')
        author_get_resp = self.client.get('/api/articles/?author=testuser', format='json')
        author = author_get_resp.data.get('results')[0]['author']['username']
        self.assertEqual('testuser', author)


    def test_title_search(self):
        user_token = self.create_user(test_user_data)
        self.client.post('/api/articles/', search_article_data, HTTP_AUTHORIZATION=user_token, format='json')
        title_get_resp = self.client.get('/api/articles/?title=hello', format='json')
        title = title_get_resp.data.get('results')[0]['title']
        self.assertEqual('hello slug', title)

    
    def test_tag_search(self):
        user_token = self.create_user(test_user_data)
        self.client.post('/api/articles/', search_article_data, HTTP_AUTHORIZATION=user_token, format='json')
        tag_get_resp = self.client.get('/api/articles/?tag=Arsenal', format='json')
        tag = tag_get_resp.data.get('results')[0]['tags']
        self.assertIn('Arsenal', tag)


    def test_keyword_search(self):
        user_token = self.create_user(test_user_data)
        self.client.post('/api/articles/', search_article_data, HTTP_AUTHORIZATION=user_token, format='json')
        keyword_get_resp = self.client.get('/api/articles/?keyword=slu', format='json')
        article_title = keyword_get_resp.data.get('results')[0]['title']
        self.assertIn('slu', article_title)
    
    def test_create_article_comment_history(self):
        user_token = self.create_user(test_user_data)
        resp = self.client.post('/api/articles/', article_data, 
                            HTTP_AUTHORIZATION=user_token, format='json')
        article_slug = resp.data['article']['slug']
        post_comment = self.client.post(f'/api/articles/{article_slug}/comments/', 
                                comment_1, HTTP_AUTHORIZATION=user_token, format='json')
        comment_id = post_comment.data["id"]
        
        self.client.put(f'/api/articles/{article_slug}/comments/{comment_id}', 
                                comment_2, HTTP_AUTHORIZATION=user_token, format='json')
        self.client.put(f'/api/articles/{article_slug}/comments/{comment_id}', 
                                comment_3, HTTP_AUTHORIZATION=user_token, format='json')
        get_comment_history = self.client.get(f'/api/comments/{comment_id}/history', 
                                HTTP_AUTHORIZATION=user_token, format='json')
   
        self.assertIn(comment_1["comment"]["body"], 
                                get_comment_history.data["history"][2]["comment_body"])
        self.assertIn(comment_2["comment"]["body"], 
                                get_comment_history.data["history"][1]["comment_body"])
        self.assertEqual(get_comment_history.data["number_of_edits"], 2)

        
    def test_user_can_bookmark_an_article(self):
        """
        Test a user can bookmark an article
        """
        user_token1 = self.create_user(register_user1_data)
        user_token2 = self.create_user(register_user2_data)
        
        response1 = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user_token1,
                                     format='json')
        response2= self.client.post('/api/articles/', article_data1, HTTP_AUTHORIZATION=user_token2,
                                     format='json')

        response3 = self.client.post(reverse('articles:create-bookmark-article',
                                             kwargs={'slug': response2.data["article"]["slug"]}),
                                     HTTP_AUTHORIZATION=user_token1,
                                     format='json'
                                     )
        self.assertEqual(response3.data["message"], "Article has been bookmarked")
        self.assertEqual(response3.status_code, status.HTTP_201_CREATED)

    def test_user_can_unbookmark_an_article(self):
        """
        Test a user can unbookmark an article
        """
        user_token1 = self.create_user(register_user1_data)
        user_token2 = self.create_user(register_user2_data)
        
        response1 = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user_token1,
                                     format='json')
        response2= self.client.post('/api/articles/', article_data1, HTTP_AUTHORIZATION=user_token2,
                                     format='json')

        response3 = self.client.post(reverse('articles:create-bookmark-article',
                                             kwargs={'slug': response2.data["article"]["slug"]}),
                                     HTTP_AUTHORIZATION=user_token1,
                                     format='json'
                                     )
        response4 = self.client.delete(reverse('articles:delete-bookmarked-article',
                                             kwargs={'slug': response2.data["article"]["slug"]}),
                                     HTTP_AUTHORIZATION=user_token1,
                                     format='json'
                                     )
        self.assertEqual(response4.data["message"], "Article has been unbookmarked")
        self.assertEqual(response4.status_code, status.HTTP_200_OK)

    def test_getting_a_list_of_bookmarked_articles(self):
        """
        Test getting all user bookmarked articles
        """
        user_token1 = self.create_user(register_user1_data)
        user_token2 = self.create_user(register_user2_data)
        
        response1 = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user_token1,
                                     format='json')
        response2= self.client.post('/api/articles/', article_data1, HTTP_AUTHORIZATION=user_token2,
                                     format='json')

        response3 = self.client.post(reverse('articles:create-bookmark-article',
                                             kwargs={'slug': response2.data["article"]["slug"]}),
                                     HTTP_AUTHORIZATION=user_token1,
                                     format='json'
                                     )
        response4 = self.client.get(reverse('articles:articles-bookmarked'),
                                     HTTP_AUTHORIZATION=user_token1,
                                     format='json'
                                     )
        self.assertEqual(response4.status_code, status.HTTP_200_OK)

    # def test_user_bookmarking_their_own_article(self):
    #     """
    #     Test user can not bookmark their artcle
    #     """
    #     user_token1 = self.create_user(register_user1_data)
    #     user_token2 = self.create_user(register_user2_data)
        
    #     response1 = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user_token1,
    #                                  format='json')
    #     response2= self.client.post('/api/articles/', article_data1, HTTP_AUTHORIZATION=user_token2,
    #                                  format='json')

    #     response3 = self.client.post(reverse('articles:create-bookmark-article',
    #                                          kwargs={'slug': response1.data["article"]["slug"]}),
    #                                  HTTP_AUTHORIZATION=user_token1,
    #                                  format='json'
    #                                  )
    #     self.assertEqual(response3.data["errors"][0], "You can not bookmark your own article")
    #     self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_bookmarking_the_same_article(self):
        """
        Test user bookmarking the same article
        """
        user_token1 = self.create_user(register_user1_data)
        user_token2 = self.create_user(register_user2_data)
        
        response1 = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user_token1,
                                     format='json')
        response2= self.client.post('/api/articles/', article_data1, HTTP_AUTHORIZATION=user_token2,
                                     format='json')

        response3 = self.client.post(reverse('articles:create-bookmark-article',
                                             kwargs={'slug': response2.data["article"]["slug"]}),
                                     HTTP_AUTHORIZATION=user_token1,
                                     format='json'
                                     )
        response4 = self.client.post(reverse('articles:create-bookmark-article',
                                             kwargs={'slug': response2.data["article"]["slug"]}),
                                     HTTP_AUTHORIZATION=user_token1,
                                     format='json'
                                     )
        self.assertEqual(response4.data["message"], "You have already bookmarked this article")
        self.assertEqual(response4.status_code, status.HTTP_200_OK)

    def test_user_can_unbookmark_an_article_that_does_not_exist(self):
        """
        Test a user can unbookmark an article that does not exist
        """
        user_token1 = self.create_user(register_user1_data)
        user_token2 = self.create_user(register_user2_data)
        
        response1 = self.client.post('/api/articles/', article_data, HTTP_AUTHORIZATION=user_token1,
                                     format='json')
        response2= self.client.post('/api/articles/', article_data1, HTTP_AUTHORIZATION=user_token2,
                                     format='json')

        response3 = self.client.post(reverse('articles:create-bookmark-article',
                                             kwargs={'slug': response2.data["article"]["slug"]}),
                                     HTTP_AUTHORIZATION=user_token1,
                                     format='json'
                                     )
        response4 = self.client.delete(reverse('articles:delete-bookmarked-article',
                                             kwargs={'slug': response2.data["article"]["slug"]}),
                                     HTTP_AUTHORIZATION=user_token1,
                                     format='json'
                                     )
        response5 = self.client.delete(reverse('articles:delete-bookmarked-article',
                                             kwargs={'slug': response2.data["article"]["slug"]}),
                                     HTTP_AUTHORIZATION=user_token1,
                                     format='json'
                                     )
       
        self.assertEqual(response5.data['error'], "Article does not exist in your bookmarks list")
        self.assertEqual(response4.status_code, status.HTTP_200_OK)






