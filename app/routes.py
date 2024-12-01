import json
from flask import Blueprint, render_template, request, redirect, url_for
from .models import db, Recipe, MealPlan  # Import your models if needed

# Define the blueprint
main = Blueprint('main', __name__)

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
        return "Invalid ingredients format. Please provide valid JSON.", 400

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
    recipe_id = int(request.form['recipe_id'])

    new_meal = MealPlan(date=date, recipe_id=recipe_id)
    db.session.add(new_meal)
    db.session.commit()

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