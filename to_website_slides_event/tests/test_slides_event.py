from odoo.tests import TransactionCase, tagged, Form


@tagged('post_install', '-at_install')
class TestSlidesEvent(TransactionCase):

    def test_compute_course_contents_on_event_form(self):
        """ Input: - Add a course on event A form
                   - In a tracks of event A add course content
            Output: a new course content line will be added to the course content lines of event A
        """
        event = self.env.ref('event.event_0')
        slide_channel = self.env.ref('website_slides.slide_channel_demo_0_gard_0')
        course_content = slide_channel.slide_ids[0]
        event.track_ids[0].slide_id = course_content
        with Form(event) as f:
            f.slide_channel_id = slide_channel
            self.assertEqual(f.slide_ids[0], course_content)
