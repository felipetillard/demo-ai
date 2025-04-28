
from typing import Annotated
from langchain.tools import tool
from dotenv import load_dotenv
import requests
import random
import os


fitness_api_key = os.getenv("EXERCISE_API_KEY")
diet_api_key = os.getenv("DIET_API_KEY")


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

        url = f"{self.base_url}/mealplanner/generate"
        params = {
            "timeFrame":time_frame,
            "diet": diet,
            "apiKey":self.api_key
        }

        response = requests.get(url, params=params)
        if not response:
            print('Meal Plan not found')
        return response.json()
    
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
def diet_tool(query: Annotated[str, "This input will either be None, vegetarian, and vegan"]):
    """use this tool to get diet plan for the user.
    The diet type provided serves as your input  \
                                        """
    dietitian_tool = Dietitian()
    result = dietitian_tool.generate_meal_plan(query)

    return result   


