# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf

class RoomForm(wtf.Form):
    # FIXME: may be required when using lastuser, since email maynot be available
    email = wtf.html5.EmailField('Your email address',
                                 validators=[wtf.Required(), wtf.Email()],
            description="An email address for contact. Not displayed anywhere")

    address = wtf.TextField('Street Address', validators=[wtf.Required()],
        description="Address of the location of your room, or in whose" + \
        "vicinity you want to search.  For better results use landmarks nearby.")
    # FIXME: May later be changed to a 'drop down'
    city = wtf.TextField('City', validators=[wtf.Required()])
    # These fields will become readonly, thanks to js.
    latitude = wtf.FloatField('Latitude', validators=[wtf.Required()])
    longitude = wtf.FloatField('Longitude', validators=[wtf.Required()])

    is_available = wtf.BooleanField('Available or Wanted?',
        description="Check this box if you have a Ghosla and are looking for tenants.")

    starting = wtf.DateField('Available/Required from',
                             description="Enter a date in yyyy-mm-dd format.",
                             validators=[wtf.Required()])

    room_type = wtf.RadioField('Room Type', coerce=int,
                                validators=[wtf.Required()],
                                choices=[
                                    (0, 'Paying Guest'),
                                    (1, '1 BHK'),
                                    (2, '2 BHK'),
                                    (3, '3 BHK'),
                                    (4, 'Studio'),
                                    (5, 'Others')
                                    ])
    room_rent = wtf.IntegerField('Rent', validators=[wtf.Required()])
    room_pref = wtf.RadioField('Tenant Preference', coerce=int,
                                choices=[
                                    (0, 'Family'),
                                    (1, 'Male'),
                                    (2, 'Female'),
                                    (3, 'Student'),
                                    (4, 'Others'),
                                ])
    room_description = wtf.TextAreaField('Description',
                    validators=[wtf.Required()],
                    description='Any additional description about the room.')

class CommentForm(wtf.Form):
    parent_id = wtf.HiddenField('Parent', default="", id="comment_parent_id")
    edit_id = wtf.HiddenField('Edit', default="", id="comment_edit_id")
    message = wtf.TextAreaField('Add comment', id="comment_message", validators=[wtf.Required()])

class DeleteCommentForm(wtf.Form):
    comment_id = wtf.HiddenField('Comment', validators=[wtf.Required()])

class ConfirmActionForm(wtf.Form):
    """
    Confirm a delete operation
    """
    # The labels on these widgets are not used. See delete.html.
    confirm = wtf.SubmitField(u"Confirm")
    cancel = wtf.SubmitField(u"Cancel")
