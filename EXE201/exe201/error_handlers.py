from exe201 import app
from flask import render_template, redirect, url_for, flash

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
@app.errorhandler(401)
def page_forbidden(e):
    flash(f'You need to login to use your service!', category='danger')
    return redirect(url_for('login_page'))