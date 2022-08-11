from django_deepcopy import django_deepcopy

from .testapp.models import Comment, Forum, Post


def test_basic_deepcopy(db):
    forum_a = Forum.objects.create(name='Forum A')
    post_1 = Post.objects.create(forum=forum_a, body='Post 1')
    comment_1_1 = Comment.objects.create(post=post_1, body='Comment 1 on Post 1')
    comment_1_2 = Comment.objects.create(post=post_1, body='Comment 2 on Post 1')
    post_2 = Post.objects.create(forum=forum_a, body='Post 2')
    comment_2_1 = Comment.objects.create(post=post_2, body='Comment 1 on Post 2')
    comment_2_2 = Comment.objects.create(post=post_2, body='Comment 2 on Post 2')

    forum_b = django_deepcopy(forum_a)

    assert set(forum_a.posts.all()) & set(forum_b.posts.all()) == set()
    forum_a_post_ids = set()
    forum_a_comment_ids = set()
    for post in forum_a.posts.all():
        forum_a_post_ids.add(post.id)
        for comment in post.comments.all():
            forum_a_comment_ids.add(comment.id)
    for post in forum_b.posts.all():
        assert post.id not in forum_a_post_ids
        for comment in post.comments.all():
            assert comment.id not in forum_a_comment_ids
