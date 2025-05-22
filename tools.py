from typing import Annotated
from langchain.tools import tool
from dotenv import load_dotenv
import requests
import random
import os
from datetime import datetime, timedelta
from langgraph.graph.ui import AnyUIMessage, push_ui_message, ui_message_reducer


load_dotenv()
fitness_api_key = os.getenv("EXERCISE_API_KEY")
diet_api_key = os.getenv("DIET_API_KEY")


#https://www.youtube.com/watch?v=dWQCzS9gbPQ

class FitnessData:

    def __init__(self):
        self.base_url = "https://api.api-ninjas.com/v1/exercises"
        self.api_key = fitness_api_key
       
    
    def get_muscle_groups_and_types(self):
     
        muscle_targets = {
                'full_body': ["abdominals", "biceps", "calves", "chest", "forearms", "glutes",
                    "hamstrings", "lower_back", "middle_back", "quadriceps",
                    "traps", "triceps", "adductors"
                    ],
                'upper_body': ["biceps", "chest", "forearms", "lats", "lower_back", "middle_back", "neck", "traps", "triceps" ],
                'lower_body': ["adductors", "calves", "glutes", "hamstrings", "quadriceps"]
            }
        exercise_types = {'types':["powerlifting","strength", "stretching", "strongman"]}

        return muscle_targets, exercise_types


    def fetch_exercises(self, type, muscle, difficulty):
        headers = {
            'X-Api-Key':self.api_key
        }
        params= {
            'type': type,
            'muscle': muscle,
            'difficulty': difficulty
            }
        try:
            response = requests.get(self.base_url, headers=headers,params=params)
            result = response.json()
            if not result:
                print(f"No exercises found for {muscle}")
            return result
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return []
        
       

    def generate_workout_plan(self, query='full_body', difficulty='intermediate'):
        output=[]
        muscle_targets, exercise_types = self.get_muscle_groups_and_types()
        muscle = random.choice(muscle_targets.get(query))
        type = random.choice(exercise_types.get('types'))
        result = self.fetch_exercises('stretching', muscle, difficulty)
        print(result)
        limit_plan = result[:3]
        for i, data in enumerate(limit_plan):
            if data not in output:
                output.append(f"Exercise {i+1}: {data['name']}")
                output.append(f"Muscle: {data['muscle']}")
                output.append(f"Instructions: {data['instructions']}")
              
        return output
            



class Dietitian:

    def __init__(self):
        self.base_url = "https://api.spoonacular.com"
        self.api_key = diet_api_key
    
    def fetch_meal(self, time_frame="day", diet="None"):
        # Hardcoded dummy meal plan data
        return {
            "meals": [
                {
                    "id": 1,
                    "title": "Vegetarian Omelette",
                    "readyInMinutes": 15,
                    "servings": 1
                },
                {
                    "id": 2,
                    "title": "Quinoa Salad",
                    "readyInMinutes": 20,
                    "servings": 2
                },
                {
                    "id": 3,
                    "title": "Grilled Tofu Stir Fry",
                    "readyInMinutes": 25,
                    "servings": 2
                }
            ],
            "nutrients": {
                "protein": 120,
                "fat": 60,
                "carbohydrates": 250
            }
        }
    
    def get_recipe_information(self, recipe_id):

        url = f"{self.base_url}/recipes/{recipe_id}/information"
        params = {"apiKey": self.api_key}
        response = requests.get(url, params=params)
        if not response:
            print("Recipe not found")
        return response.json()


    def generate_meal_plan(self, query):
        meals_processed = []
        meal_plan = self.fetch_meal(query)
        print(meal_plan)
        
        meals = meal_plan.get('meals')
        nutrients = meal_plan.get('nutrients')

        for i, meal in enumerate(meals):
            recipe_info = self.get_recipe_information(meal.get('id'))
            ingredients = [ingredient['original'] for ingredient in recipe_info.get('extendedIngredients')]

            meals_processed.append(f"🍽️ Meal {i+1}: {meal.get('title')}")
            meals_processed.append(f"Prep Time: {meal.get('readyInMinutes')}")
            meals_processed.append(f"Servings: {meal.get('servings')}")
            
    
            meals_processed.append("📝 Ingredients:\n" + "\n".join(ingredients))
            meals_processed.append(f"📋 Instructions:\n {recipe_info.get('instructions')}")
            
    
        
        meals_processed.append( 
        "\n🔢 Daily Nutrients:\n"
        f"Protein: {nutrients.get('protein', 'N/A')} kcal\n"
        f"Fat: {nutrients.get('fat', 'N/A')} g\n"
        f"Carbohydrates: {nutrients.get('carbohydrates', 'N/A')} g"
        )


        return meals_processed








@tool
def fitness_data_tool(query: Annotated[str, "This input will either be full_body, upper_body \
                                        or lower_body exercise plan"]):
    """use this tool to get fitness or workout plan for a user.
    The workout name provided serves as your input  \
                                        """
    fitness_tool = FitnessData()
    result = fitness_tool.generate_workout_plan(query)

    return result


@tool
def diet_tool(
    query: Annotated[
        str,
        "Specify the user's dietary preference: 'None' for omnivorous, 'vegetarian' for vegetarian, or 'vegan' for vegan. Use the user's nutrition plan to determine the correct value."
    ]
):
    """
    Get meal recomendation for the user based on their dietary preference and recent meal history.
    
    Input:
        - query: The user's dietary type. Acceptable values are:
            - 'None' for an omnivorous diet (no restrictions)
            - 'vegetarian' for a vegetarian diet
            - 'vegan' for a vegan diet
        This should be selected according to the user's official nutrition plan and objectives.
    
    Output:
        - A list of meal suggestions for the day, including meal names, preparation time, servings, ingredients, instructions, and daily nutrient breakdown.
    
    """
    dietitian_tool = Dietitian()
    result = dietitian_tool.generate_meal_plan(query)
    return result


@tool
def get_user_uploaded_meals(userId: Annotated[str, "The user's unique identifier (userId) - REQUIRED"], days: Annotated[int, "Number of days to look back for user-uploaded meals"]):
    """Retrieve a list of meals consumed by the user with the given userId over the past specified number of days. 
    userId is a REQUIRED argument and must be provided by the caller. Each entry includes the date, meal type (e.g., breakfast, lunch, dinner), and detailed information about the foods consumed (name, quantity, type, and status).
    """
    # Hardcoded data matching the TypeScript interfaces
    sample_data = [
        {
            "id": "day1",
            "date": "2024-06-01",
            "meal": "breakfast",
            "foods": [
                {
                    "id": "food1",
                    "name": "Oatmeal",
                    "quantity": "1 bowl",
                    "type": "carb",
                    "status": "eaten",
                    "originalName": "Oatmeal",
                    "originalQuantity": "1 bowl"
                },
                {
                    "id": "food2",
                    "name": "Banana",
                    "quantity": "1",
                    "type": "fruit",
                    "status": "eaten",
                    "originalName": "Banana",
                    "originalQuantity": "1"
                }
            ]
        },
        {
            "id": "day2",
            "date": "2024-06-02",
            "meal": "lunch",
            "foods": [
                {
                    "id": "food3",
                    "name": "Grilled Chicken",
                    "quantity": "150g",
                    "type": "protein",
                    "status": "eaten",
                    "originalName": "Grilled Chicken",
                    "originalQuantity": "150g"
                },
                {
                    "id": "food4",
                    "name": "Rice",
                    "quantity": "1 cup",
                    "type": "carb",
                    "status": "eaten",
                    "originalName": "Rice",
                    "originalQuantity": "1 cup"
                }
            ]
        },
        {
            "id": "day3",
            "date": "2024-06-03",
            "meal": "dinner",
            "foods": [
                {
                    "id": "food5",
                    "name": "Salmon",
                    "quantity": "120g",
                    "type": "protein",
                    "status": "eaten",
                    "originalName": "Salmon",
                    "originalQuantity": "120g"
                },
                {
                    "id": "food6",
                    "name": "Broccoli",
                    "quantity": "1 cup",
                    "type": "vegetable",
                    "status": "eaten",
                    "originalName": "Broccoli",
                    "originalQuantity": "1 cup"
                }
            ]
        }
    ]
    # Return the last X days (up to the length of sample_data)
    return sample_data[-days:] if days > 0 else []

@tool
def get_user_nutrition_plan(userId: Annotated[str, "The user's unique identifier (userId) - REQUIRED"]):
    """Retrieve the user's nutrition objectives and official dietary plan for the given userId.
    userId is a REQUIRED argument and must be provided by the caller. This tool returns the user's main nutrition goal (e.g., muscle gain, weight loss), daily calorie target, dietary type (e.g., omnivorous, vegetarian), any restrictions (e.g., no nuts, no sugar), number of meals per day, and country of residence.
    Use this tool to understand the user's official nutrition objectives and constraints for personalized recommendations.
    """
    return {
        "title": "Standard Muscle Gain Plan",
        "calories": 2800,
        "goal": "MUSCLE_GAIN",
        "type": "VEGETARIAN",
        "restrictions": ["NO_NUTS", "NO_SUGAR"],
        "mealAmount": 5,
        "country": "USA"
    }

@tool
def get_user_profile(userId: Annotated[str, "The user's unique identifier (userId) - REQUIRED. userId"]):
    """Retrieve the user's profile information including name, age, and country for the given userId.
    userId is a REQUIRED argument and must be provided by the caller. Use this tool to personalize recommendations and responses based on the user's demographic information.
    """
    return {
        "name": "Alex Johnson",
        "age": 29,
        "country": "USA",
        "sport":["perder peso"]
    }




@tool
def get_current_time():
    """Get the current local time in ISO 8601 format and a human-friendly string (e.g., '14:32', '2:32 PM')."""
    now = datetime.now()
    return {
        "iso": now.isoformat(),
        "24h": now.strftime("%H:%M"),
        "12h": now.strftime("%I:%M %p")
    }

@tool
def get_user_wearable_data(userId: Annotated[str, "The user's unique identifier (userId) - REQUIRED"], days: Annotated[int, "Number of days to look back for wearable data"]):
    """Retrieve wearable device data for the user with the given userId over the past specified number of days.
    Data includes steps, average heart rate, sleep duration, and calories burned for each day.
    userId is a REQUIRED argument and must be provided by the caller.
    """
    # Hardcoded sample data for demonstration
    yesterday = datetime.now() - timedelta(days=1)
    sample_data = [
        {
            "date": datetime.now(),
            "steps": 10500,
            "avg_heart_rate": 72,
            "sleep_hours": 7.5,
            "calories_burned": 2300
        },
        {
            "date": yesterday,
            "steps": 8700,
            "avg_heart_rate": 75,
            "sleep_hours": 6.8,
            "calories_burned": 2200
        },
        {
            "date": datetime.now() - timedelta(days=2),
            "steps": 12000,
            "avg_heart_rate": 70,
            "sleep_hours": 8.1,
            "calories_burned": 2450
        }
    ]
    # Return the last X days (up to the length of sample_data)
    return sample_data[-days:] if days > 0 else []

@tool
def get_user_workouts(userId: Annotated[str, "The user's unique identifier (userId) - REQUIRED"], days: Annotated[int, "Number of days to look back for user workouts"]):
    """Retrieve a list of workouts performed by the user with the given userId over the past specified number of days.
    Each workout includes the workout date, status, and detailed blocks with sets, rest, RPE, and movements (reps, duration, rest, name, muscle group, and level).
    userId is a REQUIRED argument and must be provided by the caller.
    """
    from datetime import datetime, timedelta
    
    yesterday = datetime.now() - timedelta(days=1)
    base_workouts = [
        {
            "date": datetime.now(),
            "workoutStatus": "completed",
            "blocks": [
                {
                    "blockSets": 3,
                    "blockRest": 90,
                    "blockRpe": 7,
                    "blockName": "Upper Body Strength",
                    "movements": [
                        {
                            "reps": 10,
                            "duration": None,
                            "movementRest": 60,
                            "movementName": "Push Up",
                            "movementMuscleGroup": "chest",
                            "movementLevel": 1
                        },
                        {
                            "reps": 12,
                            "duration": None,
                            "movementRest": 60,
                            "movementName": "Pull Up",
                            "movementMuscleGroup": "back",
                            "movementLevel": 2
                        }
                    ]
                }
            ]
        },
        {
            "date": yesterday,
            "workoutStatus": "skipped",
            "blocks": [
                {
                    "blockSets": 4,
                    "blockRest": 120,
                    "blockRpe": 6,
                    "blockName": "Lower Body Endurance",
                    "movements": [
                        {
                            "reps": 15,
                            "duration": None,
                            "movementRest": 45,
                            "movementName": "Squat",
                            "movementMuscleGroup": "legs",
                            "movementLevel": 1
                        },
                        {
                            "reps": None,
                            "duration": 60,
                            "movementRest": 30,
                            "movementName": "Plank",
                            "movementMuscleGroup": "core",
                            "movementLevel": 1
                        }
                    ]
                }
            ]
        },
        {
             "date": datetime.now() - timedelta(days=2),
            "workoutStatus": "completed",
            "blocks": [
                {
                    "blockSets": 2,
                    "blockRest": 60,
                    "blockRpe": 8,
                    "blockName": "HIIT Cardio",
                    "movements": [
                        {
                            "reps": None,
                            "duration": 30,
                            "movementRest": 30,
                            "movementName": "Burpees",
                            "movementMuscleGroup": "full_body",
                            "movementLevel": 2
                        },
                        {
                            "reps": None,
                            "duration": 45,
                            "movementRest": 20,
                            "movementName": "Mountain Climbers",
                            "movementMuscleGroup": "core",
                            "movementLevel": 2
                        }
                    ]
                }
            ]
        }
    ]

    return base_workouts

