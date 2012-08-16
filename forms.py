# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf

class AvailableAdForm(wtf.Form):
    email = wtf.html5.EmailField('Your email address',
                                 validators=[wtf.Required(), wtf.Email()],
            description="An email address for contact. Not displayed anywhere")

    address = wtf.TextField('Street Address', validators=[wtf.Required()],
        description="Address of the location of your acco., or in whose " + \
        "vicinity you want to search.  For better results use landmarks nearby.")

    city = wtf.TextField('City', validators=[wtf.Required()])

    # These fields will become readonly, thanks to js.
    latitude = wtf.FloatField('Latitude', validators=[wtf.Required()])
    longitude = wtf.FloatField('Longitude', validators=[wtf.Required()])

    starting = wtf.DateField('Available from',
                             description="Enter a date in yyyy-mm-dd format.",
                             validators=[wtf.Required()])

    room_type = wtf.SelectField('Acco. Type', coerce=int,
                                validators=[wtf.Required()],
                                choices=[
                                        (2, 'Paying Guest'),
                                        (3, '1 BHK'),
                                        (5, '2 BHK'),
                                        (7, '3 BHK'),
                                        (11, 'Studio'),
                                        (13, 'Others')
                                ])

    room_rent = wtf.IntegerField('Rent', description="Enter only numerals.  "
                        "A range of +/- 25% will be considered in searches?.",
            validators=[wtf.Required(),
                        wtf.NumberRange(min=0,
                                        message="Enter only numerals (0-9)")])

    room_pref = wtf.SelectMultipleField('Tenant Preference', coerce=int,
                                        choices=[
                                            (2, 'Family'),
                                            (3, 'Male'),
                                            (5, 'Female'),
                                            (7, 'Student'),
                                            (11, 'Others'),
                                        ])

    room_description = wtf.TextAreaField('Description',
                    validators=[wtf.Required(), wtf.Length(max=1024)],
                    description='Any additional description about the room.')

class WantedAdForm(AvailableAdForm):

    radius = wtf.FloatField('Radius of interest',
        description="Distance in kms. Only ads in this radius will be notified.")

    starting = wtf.DateField('Wanted from',
                             description="Enter a date in yyyy-mm-dd format.",
                             validators=[wtf.Required()])

    room_type = wtf.SelectMultipleField('Acco. Type', coerce=int,
                                        validators=[wtf.Required()],
                                        choices=[
                                            (2, 'Paying Guest'),
                                            (3, '1 BHK'),
                                            (5, '2 BHK'),
                                            (7, '3 BHK'),
                                            (11, 'Studio'),
                                            (13, 'Others')
                                        ])

    #FIXME: this should be tenant_type?
    room_pref = wtf.SelectField('Acco. required for', coerce=int,
                                choices=[
                                    (2, 'Family'),
                                    (3, 'Male'),
                                    (5, 'Female'),
                                    (7, 'Student'),
                                    (11, 'Others'),
                                ])

    room_description = wtf.TextAreaField('Description',
                    validators=[wtf.Required(), wtf.Length(max=1024)],
                    description='Any additional description of your requirements.')

class SearchForm(wtf.Form):
    pass

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
