from odoo.tests import common
from odoo.addons.website_forum.tests.common import TestForumCommon, KARMA
from odoo.exceptions import UserError, AccessError


class TestForumSecurityCommon(TestForumCommon):

    @classmethod
    def setUpClass(cls):
        super(TestForumSecurityCommon, cls).setUpClass()

        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

    @classmethod
    def create_data(cls):
        Post = cls.env['forum.post']
        cls.user_main.karma = 0
        # test case 4
        cls.own_post = Post.with_user(cls.user_main).create({
            'name': 'Post from User Moderator',
            'content': 'Who can kill me?',
            'forum_id': cls.forum.id,
        })
        cls.user_main.karma = 0
        cls.own_answer = Post.with_user(cls.user_main).create({
            'name': "Answer from user moderator",
            'forum_id': cls.forum.id,
            'parent_id': cls.own_post.id,
        })

        cls.user_member.karma = 20
        cls.another_answer = Post.with_user(cls.user_member).create({
            'name': "Answer from another user",
            'forum_id': cls.forum.id,
            'parent_id': cls.own_post.id,
        })

        cls.another_post = Post.with_user(cls.user_member).create({
            'name': 'Post from User Moderator',
            'content': 'Who can kill me?',
            'forum_id': cls.forum.id,
        })
        cls.another_post.with_user(cls.user_main).validate()

        cls.own_answer_another_post = Post.with_user(cls.user_main).create({
            'name': "Answer from user moderator",
            'forum_id': cls.forum.id,
            'parent_id': cls.another_post.id,
        })
        cls.another_answer_another_post = Post.with_user(cls.user_member).create({
            'name': "Answer from user moderator",
            'forum_id': cls.forum.id,
            'parent_id': cls.another_post.id,
        })

    def check_create_post(self):
        """User who is Forum Moderator, All Forums Moderator, or Forum Administrator can create post, them post is auto validated"""
        Post = self.env['forum.post']
        self.forum.write({
            'moderator_ids': [(4, self.user_main.id), (4, self.user_member.id)]
        })
        self.forum.invalidate_cache()
        self.user_member.karma = 0
        post3 = Post.with_user(self.user_member).create({
            'name': 'Post from Moderator User',
            'content': 'I am not a bird.',
            'forum_id': self.forum.id,
        })
        Post.with_user(self.user_member).create({
            'name': "Answer from Moderator User not enough karma",
            'forum_id': self.forum.id,
            'parent_id': post3.id,
        })

    def check_vote(self):
        """ User can't vote for himself post
            User who is Forum Moderator, All Forums Moderator, or Forum Administrator can vote with 0 karma point"""
        Vote = self.env['forum.post.vote']
        self.user_main.karma = 0
        with self.assertRaises(UserError):
            Vote.with_user(self.user_main).create({
                'post_id': self.own_post.id,
                'vote': '1',
            })
            Vote.with_user(self.user_main).create({
                'post_id': self.own_post.id,
                'vote': '-1',
            })
            Vote.with_user(self.user_main).create({
                'post_id': self.own_answer.id,
                'vote': '1',
            })
            Vote.with_user(self.user_main).create({
                'post_id': self.own_answer.id,
                'vote': '-1',
            })
        Vote.with_user(self.user_main).create({
            'post_id': self.another_post.id,
            'vote': '1',
        })
        Vote.with_user(self.user_main).write({
            'post_id': self.another_post.id,
            'vote': '-1',
        })
        Vote.with_user(self.user_main).write({
            'post_id': self.another_answer.id,
            'vote': '1',
        })
        Vote.with_user(self.user_main).write({
            'post_id': self.another_answer.id,
            'vote': '-1',
        })

    def check_edit_post(self):
        """User who is Forum Moderator, All Forums Moderator, or Forum Administrator can edit post with 0 karma point"""
        self.user_main.karma = 0
        self.own_post.with_user(self.user_main).write({'name': 'Moderator edit post'})
        self.own_answer.with_user(self.user_main).write({'name': 'Moderator edit answer'})
        self.another_answer.with_user(self.user_main).write({'name': 'Moderator edit post'})
        self.another_post.with_user(self.user_main).write({'name': 'Moderator edit post'})
        self.own_answer_another_post.with_user(self.user_main).write({'name': 'Moderator edit post'})
        self.another_answer_another_post.with_user(self.user_main).write({'name': 'Moderator edit post'})

    def check_close_post(self):
        """User who is Forum Moderator, All Forums Moderator, or Forum Administrator can close post with 0 karma point"""
        self.user_main.karma = 0
        self.own_post.with_user(self.user_main).close(None)
        self.another_post.with_user(self.user_main).close(None)

    def check_delete_post(self):
        """User who is Forum Moderator, All Forums Moderator, or Forum Administrator can delete post with 0 karma point"""
        self.user_main.karma = 0
        self.own_answer.with_user(self.user_main).unlink()
        self.another_answer.with_user(self.user_main).unlink()
        self.own_post.with_user(self.user_main).unlink()
        self.another_answer_another_post.with_user(self.user_main).unlink()
        self.own_answer_another_post.with_user(self.user_main).unlink()
        self.another_post.with_user(self.user_main).unlink()

    def check_post_toggle_correct(self):
        """User who is Forum Moderator, All Forums Moderator, or Forum Administrator can toggle is correct answer with 0 karma point"""
        self.user_main.karma = 0

        self.own_answer.with_user(self.user_main).write({'is_correct': True})
        self.another_answer.with_user(self.user_main).write({'is_correct': True})
        self.own_answer_another_post.with_user(self.user_main).write({'is_correct': True})
        self.another_answer_another_post.with_user(self.user_main).write({'is_correct': True})

    def check_comment_post(self):
        """ User who is Forum Moderator, All Forums Moderator, or Forum Administrator can comment with 0 karma point
            User who is Forum Moderator, All Forums Moderator, or Forum Administrator can unlink comment with 0 karma point"""
        self.user_main.karma = 0
        self.user_member.karma = 999
        own_comment_own_post = self.own_post.with_user(self.user_main).message_post(body='Test0', message_type='notification')
        own_comment_own_answer = self.own_answer.with_user(self.user_main).message_post(body='Test0', message_type='notification')
        own_comment_another_answer = self.another_answer.with_user(self.user_main).message_post(body='Test0', message_type='notification')
        own_comment_another_post = self.another_post.with_user(self.user_main).message_post(body='Test0', message_type='notification')
        own_comment_own_answer_another_post = self.own_answer_another_post.with_user(self.user_main).message_post(body='Test0', message_type='notification')
        own_comment_another_answer_another_post = self.another_answer_another_post.with_user(self.user_main).message_post(body='Test0', message_type='notification')

        another_comment_own_post = self.own_post.with_user(self.user_member).message_post(body='Test0', message_type='notification')
        another_comment_own_answer = self.own_answer.with_user(self.user_member).message_post(body='Test0', message_type='notification')
        another_comment_another_answer = self.another_answer.with_user(self.user_member).message_post(body='Test0', message_type='notification')
        another_comment_another_post = self.another_post.with_user(self.user_member).message_post(body='Test0', message_type='notification')
        another_comment_own_answer_another_post = self.own_answer_another_post.with_user(self.user_member).message_post(body='Test0', message_type='notification')
        another_comment_another_answer_another_post = self.another_answer_another_post.with_user(self.user_member).message_post(body='Test0', message_type='notification')

        own_comment_own_post.with_user(self.user_main).unlink()
        own_comment_own_answer.with_user(self.user_main).unlink()
        own_comment_another_answer.with_user(self.user_main).unlink()
        own_comment_another_post.with_user(self.user_main).unlink()
        own_comment_own_answer_another_post.with_user(self.user_main).unlink()
        own_comment_another_answer_another_post.with_user(self.user_main).unlink()

        another_comment_own_post.with_user(self.user_main).unlink()
        another_comment_own_answer.with_user(self.user_main).unlink()
        another_comment_another_answer.with_user(self.user_main).unlink()
        another_comment_another_post.with_user(self.user_main).unlink()
        another_comment_own_answer_another_post.with_user(self.user_main).unlink()
        another_comment_another_answer_another_post.with_user(self.user_main).unlink()

    def check_convert_answer_to_comment(self):
        """User who is Forum Moderator, All Forums Moderator, or Forum Administrator can convert answer to comment with 0 karma point"""
        self.user_main.karma = 0

        self.own_answer.with_user(self.user_main).convert_answer_to_comment()
        self.another_answer.with_user(self.user_main).convert_answer_to_comment()
        self.own_answer_another_post.with_user(self.user_main).convert_answer_to_comment()
        self.another_answer_another_post.with_user(self.user_main).convert_answer_to_comment()

    def check_convert_comment_to_answer(self):
        """User who is Forum Moderator, All Forums Moderator, or Forum Administrator can convert comment to answer with 0 karma point"""
        self.user_main.karma = 0
        self.user_member.karma = 999
        own_comment_own_post = self.own_post.with_user(self.user_main).message_post(body='Test0', message_type='notification')
        own_comment_own_answer = self.own_answer.with_user(self.user_main).message_post(body='Test0', message_type='notification')
        own_comment_another_answer = self.another_answer.with_user(self.user_main).message_post(body='Test0', message_type='notification')
        own_comment_another_post = self.another_post.with_user(self.user_main).message_post(body='Test0', message_type='notification')
        own_comment_own_answer_another_post = self.own_answer_another_post.with_user(self.user_main).message_post(body='Test0', message_type='notification')
        own_comment_another_answer_another_post = self.another_answer_another_post.with_user(self.user_main).message_post(body='Test0', message_type='notification')

        another_comment_own_post = self.own_post.with_user(self.user_member).message_post(body='Test0', message_type='notification')
        another_comment_own_answer = self.own_answer.with_user(self.user_member).message_post(body='Test0', message_type='notification')
        another_comment_another_answer = self.another_answer.with_user(self.user_member).message_post(body='Test0', message_type='notification')
        another_comment_another_post = self.another_post.with_user(self.user_member).message_post(body='Test0', message_type='notification')
        another_comment_own_answer_another_post = self.own_answer_another_post.with_user(self.user_member).message_post(body='Test0', message_type='notification')
        another_comment_another_answer_another_post = self.another_answer_another_post.with_user(self.user_member).message_post(body='Test0', message_type='notification')

        self.own_post.with_user(self.user_main).convert_comment_to_answer(own_comment_own_post.id)
        self.own_post.with_user(self.user_main).convert_comment_to_answer(own_comment_own_answer.id)
        self.own_post.with_user(self.user_main).convert_comment_to_answer(own_comment_another_answer.id)
        self.own_post.with_user(self.user_main).convert_comment_to_answer(another_comment_own_post.id)
        self.own_post.with_user(self.user_main).convert_comment_to_answer(another_comment_own_answer.id)
        self.own_post.with_user(self.user_main).convert_comment_to_answer(another_comment_another_answer.id)

        self.another_post.with_user(self.user_main).convert_comment_to_answer(own_comment_another_post.id)
        self.another_post.with_user(self.user_main).convert_comment_to_answer(own_comment_own_answer_another_post.id)
        self.another_post.with_user(self.user_main).convert_comment_to_answer(own_comment_another_answer_another_post.id)
        self.another_post.with_user(self.user_main).convert_comment_to_answer(another_comment_another_post.id)
        self.another_post.with_user(self.user_main).convert_comment_to_answer(another_comment_own_answer_another_post.id)
        self.another_post.with_user(self.user_main).convert_comment_to_answer(another_comment_another_answer_another_post.id)

    def check_attach_link_image(self):
        """User who is Forum Moderator, All Forums Moderator, or Forum Administrator can attack link and image in post with 0 karma point"""
        self.user_main.karma = 0
        Post = self.env['forum.post']
        Post.with_user(self.user_main).create({
            'name': 'Post from User Moderator',
            'content': '<p>test answer <img class="img-fluid o_we_custom_image" src="/website/static/src/img/snippets_demo/s_team_member_4.png"></p><p><a href="http://www.google.com" target="_blank">link</a><br></p>',
            'forum_id': self.forum.id,
        })

    def check_flag(self):
        """User who is Forum Moderator, All Forums Moderator, or Forum Administrator can a flag post with 0 karma point"""
        self.user_main.karma = 0

        self.own_post.with_user(self.user_main).flag()
        self.own_answer.with_user(self.user_main).flag()
        self.another_answer.with_user(self.user_main).flag()
        self.another_post.with_user(self.user_main).flag()
        self.own_answer_another_post.with_user(self.user_main).flag()
        self.another_answer_another_post.with_user(self.user_main).flag()

    def check_mark_a_post_as_offensive(self):
        """User who is Forum Moderator, All Forums Moderator, or Forum Administrator can mark a post as offensive with 0 karma point"""
        self.user_main.karma = 0

        self.own_answer.with_user(self.user_main).flag()
        self.another_answer.with_user(self.user_main).flag()
        self.own_answer_another_post.with_user(self.user_main).flag()
        self.another_answer_another_post.with_user(self.user_main).flag()

        self.own_answer.with_user(self.user_main).mark_as_offensive(12)
        self.another_answer.with_user(self.user_main).validate()
        self.own_post.with_user(self.user_main).flag()
        self.own_post.with_user(self.user_main).validate()
        self.own_answer_another_post.with_user(self.user_main).mark_as_offensive(12)
        self.another_answer_another_post.with_user(self.user_main).validate()
        self.another_post.with_user(self.user_main).flag()
        self.another_post.with_user(self.user_main).mark_as_offensive(12)

    def check_tag(self):
        """User who is Forum Moderator, All Forums Moderator, or Forum Administrator can create tags or change tags on a post with 0 karma point"""
        self.user_main.karma = 0

        self.own_post.with_user(self.user_main).write({
            'tag_ids': [(0, 0, {'name': 'Tagtest999', 'forum_id': self.forum.id})]
        })
        self.another_post.with_user(self.user_main).write({
            'tag_ids': [(0, 0, {'name': 'Tagtest9999', 'forum_id': self.forum.id})]
        })

    def check_delete_permission(self):
        """Remove user_main from a forum's moderators list. Check if user_main should follows karma base as normal users."""
        Post = self.env['forum.post']

        self.forum.write({
            'moderator_ids': [(3, self.user_main.id)]
        })
        self.forum.invalidate_cache()
        self.user_main.karma = 0
        with self.assertRaises(AccessError):
            crash_post = Post.with_user(self.user_main).create({
                'name': 'Post from User user 2',
                'content': 'Who can kill me?',
                'forum_id': self.forum.id
            })
        self.user_main.karma = 999
        success_post = Post.with_user(self.user_main).create({
            'name': 'Post from User user 2',
            'content': 'Who can kill me?',
            'forum_id': self.forum.id
        })

    def check_post_on_another_forum(self):
        """ user_main is moderator of forum, but is't moderator of forum_test
            If user_main does not have enough karma points, user_main can't create posts on forum_test"""
        Forum = self.env['forum.forum']
        Post = self.env['forum.post']
        self.forum_test = Forum.create({
            'name': 'TestForum'
        })
        self.user_main.karma = 0
        self.user_member.karma = 0
        self.forum_test.moderator_ids = self.user_member
        self.user_member_post = Post.with_user(self.user_member).create({
            'name': 'Post from user member',
            'content': 'Who can kill me?',
            'forum_id': self.forum_test.id
        })
        with self.assertRaises(AccessError):
            self.crash_post = Post.with_user(self.user_main).create({
                'name': 'Post from User user 2',
                'content': 'Who can kill me?',
                'forum_id': self.forum_test.id
            })
            self.crash_answer = Post.with_user(self.user_main).create({
                'name': "Answer from another user",
                'forum_id': self.forum.id,
                'parent_id': self.user_member_post.id,
            })

    def check_create_forum(self):
        """User who is Administrator can create forums. This user can create posts, and those posts will be validated automatically"""
        Forum = self.env['forum.forum']
        Post = self.env['forum.post']
        self.forum_test = Forum.with_user(self.user_main).create({
            'name': 'TestForum'
        })
        Post.with_user(self.user_main).create({
            'name': 'Post from User Moderator',
            'content': 'Who can kill me?',
            'forum_id': self.forum_test.id,
        })
