from app import app, db, User, Post
from faker import Faker

fake = Faker()

# Replace this with an existing user ID from your database
user_id = 'any_id'

# Number of fake posts to generate
num_posts = 200

with app.app_context():
    for _ in range(num_posts):
        title = fake.sentence()
        content = fake.paragraph(nb_sentences=10, variable_nb_sentences=True)
        post = Post(title=title, content=content, user_id=user_id)
        db.session.add(post)

    db.session.commit()
