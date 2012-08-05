Hello {{ user.fullname }},

We have found a tenant for you!

{{ url_for('view_ad', url=room.urlname, _external=True) }}

{# FIXME: What should be the content here? #}
