from flask import Flask, render_template, flash, redirect, url_for, session, request
import logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, IntegerField, validators
from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__)


# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Jashboy@06'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)

# Index
@app.route('/')
def index():
    return render_template('home.html')
 
 #explore
@app.route('/commodities/<string:product>/')
def product(product):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get articles
    result= cur.execute("SELECT * FROM articles WHERE product= %s" , [product] )

    articles = cur.fetchall()

    if result > 0:
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)
    # Close connection
    cur.close()
    

# Mandi Price
@app.route('/Mandi Price')
def mandi():
    return render_template('mandi.html')

# Mandi Price
@app.route('/protip')
def protip():
    return render_template('protip.html')

# commodities
@app.route('/commodities')
def articles():
    return render_template('explore copy.html')
   

#Single Article
@app.route('/commodities/<string:product>/article/<string:name>')
def article(name,product):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article
    cur.execute("SELECT * FROM articles WHERE name = %s", [name])

    article = cur.fetchone()

    return render_template('article.html', article=article)


# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    mobile_no=IntegerField('mobile no')
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    address=TextAreaField('address')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get articles
    #result = cur.execute("SELECT * FROM articles")
    # Show articles only from the user logged in 
    result = cur.execute("SELECT * FROM articles WHERE name = %s",[session['username']])

    articles = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg)
    # Close connection
    cur.close()

# Article Form Class
class ArticleForm(Form):
    name=StringField('Name', [validators.Length(min=1,max=30)])
    product = StringField('Product', [validators.Length(min=1, max=25)])
    variety = StringField('Variety', [validators.Length(min=1, max=50)])
    packaging_type = StringField('Packaging Type', [validators.Length(min=1, max=50)])
    packaging_size= StringField('Packaging Size')
    quantity_expected = StringField('Quantity Expected')
    quality_expected = StringField('Quality Expected', [validators.Length(min=1, max=50)])
    price = StringField('Price')
    state = StringField('State', [validators.Length(min=1, max=50)])
    productid=StringField('product_id')
   

# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        product = form.product.data
        variety = form.variety.data
        packaging_type = form.packaging_type.data
        packaging_size = form.packaging_size.data
        quantity_expected = form.quantity_expected.data
        quality_expected = form.quality_expected.data
        price = form.price.data
        state = form.state.data
        

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO articles(name, product, variety, packaging_type, packaging_size, quantity_expected, quality_expected, price, state) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)",(name, product, variety, packaging_type, packaging_size, quantity_expected, quality_expected, price, state))

        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('Article Created', 'success')

        return redirect(url_for('dashboard'))
    
    return render_template('add_article.html', form=form)


# Edit Article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article by id
    cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()
    cur.close()
    # Get form
    form = ArticleForm(request.form)

    # Populate article form fields
    form.name.data=article['name']
    form.product.data=article['product']
    form.variety.data=article['variety']
    form.packaging_type.data=article['packaging_type']
    form.packaging_size.data=article['packaging_size']
    form.quantity_expected.data=article['quantity_expected']
    form.quality_expected.data=article['quality_expected']
    form.price.data=article['price']
    form.state.data=article['state']

    if request.method == 'POST' and form.validate():
       
        name = request.form['name']
        product = request.form['product']
        variety = request.form['variety']
        packaging_type = request.form['packaging_type']
        packaging_size = request.form['packaging_size']
        quantity_expected = request.form['quantity_expected']
        quality_expexted = request.form['quality_expected']
        price = request.form['price']
        state = request.form['state']

        # Create Cursor
        cur = mysql.connection.cursor()
        
      
        # Execute
        cur.execute ("UPDATE articles SET name=%s, product=%s, variety=%s, packaging_type=%s,packaging_size=%s, quantity_expected=%s, quality_expected=%s, price=%s,state=%s WHERE id=%s",(name, product, variety, packaging_type,packaging_size,quantity_expected,quality_expexted,price,state))
        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('Product Updated', 'success')

        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', form=form)


# Delete Article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM articles WHERE id = %s", [id])

    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    flash('Article Deleted', 'success')

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)