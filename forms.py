# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf

class RoomForm(wtf.Form):
    # FIXME: may be required when using lastuser, since email maynot be available
    email = wtf.html5.EmailField('Your email address', 
                                 validators=[wtf.Required()],
            description="An email address for contact. Not displayed anywhere")
