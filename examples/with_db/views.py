import logging
import sqlalchemy

import rowan.core.http as http

import models

def view_blog(request):
    """Displays the latest blog entries on one page."""
    logging.getLogger('view_blog').debug('Called')
    
    # Look up the entries.
    session = request.services.db()
    entries = session.query(models.BlogEntry).order_by(
        sqlalchemy.desc(models.BlogEntry.date)
        )[:5]
    
    # Load the template and render
    template = request.services.templates.get_template('view_blog.html')
    content = template.render(entries=entries)
    return http.HttpResponse(content.encode('ascii', 'ignore'))