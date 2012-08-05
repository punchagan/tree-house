Hello {{ user.fullname }},

We have found a room for you!

{{ url_for('view_ad', url=room.urlname) }}

{# FIXME: What should be the content here? #}
