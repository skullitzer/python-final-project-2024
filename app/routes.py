import json
from flask import Blueprint, render_template, request, redirect, url_for
from .models import db, Recipe, MealPlan  # Import your models if needed
from functools import wraps
from flask import request, jsonify
from datetime import datetime

# Define the blueprint
main = Blueprint('main', __name__)

BLOCKED_IPS = {'127.0.0.1'}  # Add IPs you want to block

def check_ip(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        client_ip = request.remote_addr
        print(f"Incoming request from IP: {client_ip}")  # Log incoming IP
        if client_ip in BLOCKED_IPS:
            print(f"Blocked request from IP: {client_ip}")  # Log blocked IP
            return jsonify({'error': 'Your IP is blocked.'}), 403
        return f(*args, **kwargs)
    return wrapper

@main.route('/')
def home():
    return render_template('base.html')

@main.route('/recipes')
def list_recipes():

    # Print when the route is hit
    print("GET /shopping_list endpoint hit.")

    recipes = Recipe.query.all()

    # Print before returning results
    print(f"Returning recipes: {recipes}")

    return render_template('recipes.html', recipes=recipes)

@main.route('/add_recipe')
def add_recipe():
    return render_template('add_recipe.html')

@main.route('/save_recipe', methods=['POST'])
def save_recipe():
    name = request.form['name']
    instructions = request.form['instructions']
    category = request.form['category']

    # Print before processing ingredients
    print(f"Received ingredients: {request.form['ingredients']}")

    # Validate the ingredients field
    try:
        ingredients = json.loads(request.form['ingredients'])  # Validate JSON
        # If the JSON is valid, convert it back to a string for storage
        ingredients = json.dumps(ingredients)
    except json.JSONDecodeError as e:
        # Print error details
        print(f"Error parsing ingredients JSON: {str(e)}")
        # Pass an error message to the add_recipe.html template
        return render_template('add_recipe.html', error="Invalid JSON format for ingredients. Please fix it.")

    new_recipe = Recipe(name=name, ingredients=ingredients, instructions=instructions, category=category)

    # Print before inserting into the database
    print(f"Inserting recipe into database: {new_recipe}")

    db.session.add(new_recipe)
    db.session.commit()

    # Print after the commit
    print(f"Recipe {new_recipe.name} successfully saved to database.")

    return redirect(url_for('main.list_recipes'))

@main.route('/meal_calendar')
def meal_calendar():
    meals = MealPlan.query.all()
    return render_template('meal_calendar.html', meals=meals)

@main.route('/add_meal', methods=['POST'])
def add_meal():
    date = request.form['date']
    recipe_id = request.form['recipe_id']

    # Validate date format
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        print(f"Invalid date format: {date}")
        return render_template('meal_calendar.html', error="Invalid date format. Please use YYYY-MM-DD.", meals=MealPlan.query.all())

    # Validate recipe ID
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        print(f"Recipe ID does not exist: {recipe_id}")
        return render_template('meal_calendar.html', error="Recipe ID does not exist. Please enter a valid ID.", meals=MealPlan.query.all())

    # Save the meal if validations pass
    new_meal = MealPlan(date=date, recipe_id=recipe_id)
    db.session.add(new_meal)
    db.session.commit()

    print(f"Meal added: {new_meal}")
    return redirect(url_for('main.meal_calendar'))

@main.route('/shopping_list')
def shopping_list():
    meal_plans = MealPlan.query.all()

    # Print when the route is hit
    print("GET /shopping_list endpoint hit.")

    shopping_list = {}

    for meal in meal_plans:
        recipe = Recipe.query.get(meal.recipe_id)
        ingredients = json.loads(recipe.ingredients)  # Safely parse JSON

        for item in ingredients:
            ingredient = item['ingredient']
            quantity = item['quantity']

            # Accumulate quantities for each ingredient
            if ingredient in shopping_list:
                shopping_list[ingredient].append(quantity)
            else:
                shopping_list[ingredient] = [quantity]

    # Combine quantities into a single string
    combined_list = {key: ", ".join(values) for key, values in shopping_list.items()}

    return render_template('shopping_list.html', shopping_list=combined_list)

@main.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    # Print when the delete endpoint is hit
    print(f"DELETE /delete_recipe/{recipe_id} endpoint hit.")

    # Fetch the recipe by ID
    recipe = Recipe.query.get_or_404(recipe_id)

    # Print before deleting related records
    print(f"Deleting related meal plans for recipe_id: {recipe_id}")

    # Delete all associated meal plans
    MealPlan.query.filter_by(recipe_id=recipe_id).delete()

    # Print before deleting the recipe
    print(f"Deleting recipe: {recipe}")

    # Delete the recipe
    db.session.delete(recipe)
    db.session.commit()

    # Print after successful deletion
    print(f"Recipe with ID {recipe_id} successfully deleted.")

    # Redirect back to the recipes page
    return redirect(url_for('main.list_recipes'))

@main.route('/api/recipes', methods=['GET'])
@check_ip
def get_recipes():
    # Fetch recipes logic
    recipes = Recipe.query.all()
    return jsonify({'recipes': [recipe.name for recipe in recipes]})