import os
import re
from pathlib import Path

from openai import OpenAI

PROMPT_FILE = Path(__file__).parent / "meal_plan_prompt.md"


def main():
	print("\n=== 7-Day South Indian Vegetarian Meal Planner ===\n")

	try:
		age = int(input("Enter your age (18-100): "))
		if not 18 <= age <= 100:
			print("Please enter an age between 18 and 100.")
			return
	except ValueError:
		print("Invalid age. Please enter a number.")
		return

	goal = input("Enter your goal (e.g. weight loss): ").strip()
	if not goal:
		print("Please enter a goal.")
		return

	if not PROMPT_FILE.exists():
		print("Error: meal_plan_prompt.md file not found.")
		return

	prompt = PROMPT_FILE.read_text(encoding="utf-8")

	# Change only the Age and Goal fields in the FOR block.
	parts = re.split(r"(?=^## ROLE\b)", prompt, maxsplit=1, flags=re.M)

	if len(parts) != 2:
		print("Error: The prompt must contain a ## ROLE section.")
		return

	profile, instructions = parts

	profile, age_count = re.subn(
		r"(?im)^(\s*-\s*)?Age\s*:\s*.*$",
		f"- Age: {age} years",
		profile,
		count=1,
	)

	profile, goal_count = re.subn(
		r"(?im)^(\s*-\s*)?Goal\s*:\s*.*$",
		f"- Goal: {goal}",
		profile,
		count=1,
	)

	if age_count != 1 or goal_count != 1:
		print("Error: The FOR block needs Age: and Goal: fields.")
		return

	prompt = profile + instructions

	if not os.getenv("OPENAI_API_KEY"):
		print("Error: OPENAI_API_KEY is not configured.")
		return

	print("\nGenerating your 7-day meal plan...\n")

	try:
		client = OpenAI()

		response = client.responses.create(
			model="gpt-4.1-mini",
			instructions=(
				"Follow the supplied meal-planning prompt. "
				"Respect allergies and dietary restrictions. "
				"Produce a 28-row Markdown table with the columns "
				"Day | Meal | Dish | Portion. "
				"Do not invent medical details."
			),
			input=prompt,
		)

		print(response.output_text or "No meal plan returned.")

	except Exception as error:
		print(f"API request failed: {error}")


if __name__ == "__main__":
	main()