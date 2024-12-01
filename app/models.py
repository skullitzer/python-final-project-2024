from . import db

# Recipe Model
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)  # JSON string for ingredient details
    instructions = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))

# Meal Plan Model
class MealPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)  # Format: YYYY-MM-DD
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe = db.relationship('Recipe', backref='meal_plans')