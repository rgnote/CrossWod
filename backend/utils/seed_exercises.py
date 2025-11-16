from sqlalchemy.orm import Session
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
from models.database import Exercise


def seed_exercises():
    """Seed the database with common exercises"""
    db = SessionLocal()

    # Check if already seeded
    if db.query(Exercise).filter(Exercise.is_custom == False).count() > 0:
        db.close()
        return

    exercises = [
        # CHEST - Push
        {"name": "Barbell Bench Press", "category": "push", "muscle_groups": ["chest", "triceps", "shoulders"], "equipment": "barbell"},
        {"name": "Incline Barbell Bench Press", "category": "push", "muscle_groups": ["chest", "triceps", "shoulders"], "equipment": "barbell"},
        {"name": "Decline Barbell Bench Press", "category": "push", "muscle_groups": ["chest", "triceps"], "equipment": "barbell"},
        {"name": "Dumbbell Bench Press", "category": "push", "muscle_groups": ["chest", "triceps", "shoulders"], "equipment": "dumbbell"},
        {"name": "Incline Dumbbell Press", "category": "push", "muscle_groups": ["chest", "triceps", "shoulders"], "equipment": "dumbbell"},
        {"name": "Dumbbell Flyes", "category": "push", "muscle_groups": ["chest"], "equipment": "dumbbell"},
        {"name": "Cable Flyes", "category": "push", "muscle_groups": ["chest"], "equipment": "cable"},
        {"name": "Push-Ups", "category": "push", "muscle_groups": ["chest", "triceps", "shoulders"], "equipment": "bodyweight"},
        {"name": "Diamond Push-Ups", "category": "push", "muscle_groups": ["chest", "triceps"], "equipment": "bodyweight"},
        {"name": "Chest Dips", "category": "push", "muscle_groups": ["chest", "triceps", "shoulders"], "equipment": "bodyweight"},
        {"name": "Machine Chest Press", "category": "push", "muscle_groups": ["chest", "triceps"], "equipment": "machine"},
        {"name": "Pec Deck Machine", "category": "push", "muscle_groups": ["chest"], "equipment": "machine"},

        # SHOULDERS - Push
        {"name": "Overhead Press", "category": "push", "muscle_groups": ["shoulders", "triceps"], "equipment": "barbell"},
        {"name": "Dumbbell Shoulder Press", "category": "push", "muscle_groups": ["shoulders", "triceps"], "equipment": "dumbbell"},
        {"name": "Arnold Press", "category": "push", "muscle_groups": ["shoulders", "triceps"], "equipment": "dumbbell"},
        {"name": "Lateral Raises", "category": "push", "muscle_groups": ["shoulders"], "equipment": "dumbbell"},
        {"name": "Front Raises", "category": "push", "muscle_groups": ["shoulders"], "equipment": "dumbbell"},
        {"name": "Rear Delt Flyes", "category": "pull", "muscle_groups": ["shoulders", "back"], "equipment": "dumbbell"},
        {"name": "Face Pulls", "category": "pull", "muscle_groups": ["shoulders", "back"], "equipment": "cable"},
        {"name": "Upright Rows", "category": "pull", "muscle_groups": ["shoulders", "back"], "equipment": "barbell"},
        {"name": "Cable Lateral Raises", "category": "push", "muscle_groups": ["shoulders"], "equipment": "cable"},
        {"name": "Machine Shoulder Press", "category": "push", "muscle_groups": ["shoulders", "triceps"], "equipment": "machine"},

        # TRICEPS - Push
        {"name": "Tricep Dips", "category": "push", "muscle_groups": ["triceps", "chest"], "equipment": "bodyweight"},
        {"name": "Close-Grip Bench Press", "category": "push", "muscle_groups": ["triceps", "chest"], "equipment": "barbell"},
        {"name": "Skull Crushers", "category": "push", "muscle_groups": ["triceps"], "equipment": "barbell"},
        {"name": "Tricep Pushdowns", "category": "push", "muscle_groups": ["triceps"], "equipment": "cable"},
        {"name": "Overhead Tricep Extension", "category": "push", "muscle_groups": ["triceps"], "equipment": "dumbbell"},
        {"name": "Rope Pushdowns", "category": "push", "muscle_groups": ["triceps"], "equipment": "cable"},
        {"name": "Kickbacks", "category": "push", "muscle_groups": ["triceps"], "equipment": "dumbbell"},

        # BACK - Pull
        {"name": "Deadlift", "category": "pull", "muscle_groups": ["back", "hamstrings", "glutes"], "equipment": "barbell"},
        {"name": "Barbell Rows", "category": "pull", "muscle_groups": ["back", "biceps"], "equipment": "barbell"},
        {"name": "Pendlay Rows", "category": "pull", "muscle_groups": ["back", "biceps"], "equipment": "barbell"},
        {"name": "Dumbbell Rows", "category": "pull", "muscle_groups": ["back", "biceps"], "equipment": "dumbbell"},
        {"name": "Pull-Ups", "category": "pull", "muscle_groups": ["back", "biceps"], "equipment": "bodyweight"},
        {"name": "Chin-Ups", "category": "pull", "muscle_groups": ["back", "biceps"], "equipment": "bodyweight"},
        {"name": "Lat Pulldowns", "category": "pull", "muscle_groups": ["back", "biceps"], "equipment": "cable"},
        {"name": "Seated Cable Rows", "category": "pull", "muscle_groups": ["back", "biceps"], "equipment": "cable"},
        {"name": "T-Bar Rows", "category": "pull", "muscle_groups": ["back", "biceps"], "equipment": "barbell"},
        {"name": "Chest Supported Rows", "category": "pull", "muscle_groups": ["back", "biceps"], "equipment": "dumbbell"},
        {"name": "Straight Arm Pulldowns", "category": "pull", "muscle_groups": ["back"], "equipment": "cable"},
        {"name": "Rack Pulls", "category": "pull", "muscle_groups": ["back", "hamstrings"], "equipment": "barbell"},
        {"name": "Good Mornings", "category": "pull", "muscle_groups": ["back", "hamstrings"], "equipment": "barbell"},
        {"name": "Hyperextensions", "category": "pull", "muscle_groups": ["back", "glutes"], "equipment": "bodyweight"},

        # BICEPS - Pull
        {"name": "Barbell Curls", "category": "pull", "muscle_groups": ["biceps"], "equipment": "barbell"},
        {"name": "Dumbbell Curls", "category": "pull", "muscle_groups": ["biceps"], "equipment": "dumbbell"},
        {"name": "Hammer Curls", "category": "pull", "muscle_groups": ["biceps", "forearms"], "equipment": "dumbbell"},
        {"name": "Preacher Curls", "category": "pull", "muscle_groups": ["biceps"], "equipment": "barbell"},
        {"name": "Incline Dumbbell Curls", "category": "pull", "muscle_groups": ["biceps"], "equipment": "dumbbell"},
        {"name": "Concentration Curls", "category": "pull", "muscle_groups": ["biceps"], "equipment": "dumbbell"},
        {"name": "Cable Curls", "category": "pull", "muscle_groups": ["biceps"], "equipment": "cable"},
        {"name": "EZ Bar Curls", "category": "pull", "muscle_groups": ["biceps"], "equipment": "barbell"},
        {"name": "Spider Curls", "category": "pull", "muscle_groups": ["biceps"], "equipment": "dumbbell"},

        # LEGS - Quadriceps
        {"name": "Barbell Squats", "category": "legs", "muscle_groups": ["quadriceps", "glutes", "hamstrings"], "equipment": "barbell"},
        {"name": "Front Squats", "category": "legs", "muscle_groups": ["quadriceps", "core"], "equipment": "barbell"},
        {"name": "Leg Press", "category": "legs", "muscle_groups": ["quadriceps", "glutes"], "equipment": "machine"},
        {"name": "Hack Squats", "category": "legs", "muscle_groups": ["quadriceps"], "equipment": "machine"},
        {"name": "Goblet Squats", "category": "legs", "muscle_groups": ["quadriceps", "glutes"], "equipment": "dumbbell"},
        {"name": "Bulgarian Split Squats", "category": "legs", "muscle_groups": ["quadriceps", "glutes"], "equipment": "dumbbell"},
        {"name": "Walking Lunges", "category": "legs", "muscle_groups": ["quadriceps", "glutes"], "equipment": "dumbbell"},
        {"name": "Leg Extensions", "category": "legs", "muscle_groups": ["quadriceps"], "equipment": "machine"},
        {"name": "Sissy Squats", "category": "legs", "muscle_groups": ["quadriceps"], "equipment": "bodyweight"},
        {"name": "Box Squats", "category": "legs", "muscle_groups": ["quadriceps", "glutes"], "equipment": "barbell"},

        # LEGS - Hamstrings
        {"name": "Romanian Deadlifts", "category": "legs", "muscle_groups": ["hamstrings", "glutes"], "equipment": "barbell"},
        {"name": "Stiff-Leg Deadlifts", "category": "legs", "muscle_groups": ["hamstrings", "glutes"], "equipment": "barbell"},
        {"name": "Lying Leg Curls", "category": "legs", "muscle_groups": ["hamstrings"], "equipment": "machine"},
        {"name": "Seated Leg Curls", "category": "legs", "muscle_groups": ["hamstrings"], "equipment": "machine"},
        {"name": "Nordic Curls", "category": "legs", "muscle_groups": ["hamstrings"], "equipment": "bodyweight"},
        {"name": "Single-Leg Romanian Deadlifts", "category": "legs", "muscle_groups": ["hamstrings", "glutes"], "equipment": "dumbbell"},
        {"name": "Glute-Ham Raises", "category": "legs", "muscle_groups": ["hamstrings", "glutes"], "equipment": "machine"},

        # LEGS - Glutes
        {"name": "Hip Thrusts", "category": "legs", "muscle_groups": ["glutes", "hamstrings"], "equipment": "barbell"},
        {"name": "Glute Bridges", "category": "legs", "muscle_groups": ["glutes"], "equipment": "bodyweight"},
        {"name": "Cable Pull-Throughs", "category": "legs", "muscle_groups": ["glutes", "hamstrings"], "equipment": "cable"},
        {"name": "Sumo Deadlifts", "category": "legs", "muscle_groups": ["glutes", "hamstrings", "quadriceps"], "equipment": "barbell"},
        {"name": "Step-Ups", "category": "legs", "muscle_groups": ["glutes", "quadriceps"], "equipment": "dumbbell"},

        # LEGS - Calves
        {"name": "Standing Calf Raises", "category": "legs", "muscle_groups": ["calves"], "equipment": "machine"},
        {"name": "Seated Calf Raises", "category": "legs", "muscle_groups": ["calves"], "equipment": "machine"},
        {"name": "Donkey Calf Raises", "category": "legs", "muscle_groups": ["calves"], "equipment": "machine"},
        {"name": "Single-Leg Calf Raises", "category": "legs", "muscle_groups": ["calves"], "equipment": "bodyweight"},

        # CORE
        {"name": "Plank", "category": "core", "muscle_groups": ["core"], "equipment": "bodyweight"},
        {"name": "Side Plank", "category": "core", "muscle_groups": ["core"], "equipment": "bodyweight"},
        {"name": "Crunches", "category": "core", "muscle_groups": ["core"], "equipment": "bodyweight"},
        {"name": "Hanging Leg Raises", "category": "core", "muscle_groups": ["core", "hip_flexors"], "equipment": "bodyweight"},
        {"name": "Cable Woodchops", "category": "core", "muscle_groups": ["core"], "equipment": "cable"},
        {"name": "Russian Twists", "category": "core", "muscle_groups": ["core"], "equipment": "bodyweight"},
        {"name": "Ab Wheel Rollouts", "category": "core", "muscle_groups": ["core"], "equipment": "other"},
        {"name": "Dead Bug", "category": "core", "muscle_groups": ["core"], "equipment": "bodyweight"},
        {"name": "Bird Dog", "category": "core", "muscle_groups": ["core", "back"], "equipment": "bodyweight"},
        {"name": "Mountain Climbers", "category": "core", "muscle_groups": ["core", "hip_flexors"], "equipment": "bodyweight"},
        {"name": "Bicycle Crunches", "category": "core", "muscle_groups": ["core"], "equipment": "bodyweight"},
        {"name": "V-Ups", "category": "core", "muscle_groups": ["core"], "equipment": "bodyweight"},
        {"name": "Dragon Flags", "category": "core", "muscle_groups": ["core"], "equipment": "bodyweight"},
        {"name": "L-Sit", "category": "core", "muscle_groups": ["core", "hip_flexors"], "equipment": "bodyweight"},

        # CARDIO
        {"name": "Running", "category": "cardio", "muscle_groups": ["quadriceps", "hamstrings", "calves"], "equipment": "none"},
        {"name": "Cycling", "category": "cardio", "muscle_groups": ["quadriceps", "hamstrings"], "equipment": "machine"},
        {"name": "Rowing Machine", "category": "cardio", "muscle_groups": ["back", "biceps", "core"], "equipment": "machine"},
        {"name": "Jump Rope", "category": "cardio", "muscle_groups": ["calves", "shoulders"], "equipment": "other"},
        {"name": "Stair Climber", "category": "cardio", "muscle_groups": ["quadriceps", "glutes"], "equipment": "machine"},
        {"name": "Elliptical", "category": "cardio", "muscle_groups": ["quadriceps", "hamstrings"], "equipment": "machine"},
        {"name": "Swimming", "category": "cardio", "muscle_groups": ["full_body"], "equipment": "none"},
        {"name": "Battle Ropes", "category": "cardio", "muscle_groups": ["shoulders", "core"], "equipment": "other"},
        {"name": "Box Jumps", "category": "cardio", "muscle_groups": ["quadriceps", "glutes", "calves"], "equipment": "other"},
        {"name": "Burpees", "category": "cardio", "muscle_groups": ["full_body"], "equipment": "bodyweight"},
        {"name": "Jumping Jacks", "category": "cardio", "muscle_groups": ["full_body"], "equipment": "bodyweight"},
        {"name": "High Knees", "category": "cardio", "muscle_groups": ["hip_flexors", "calves"], "equipment": "bodyweight"},
        {"name": "Sprints", "category": "cardio", "muscle_groups": ["quadriceps", "hamstrings", "glutes"], "equipment": "none"},

        # OLYMPIC LIFTS
        {"name": "Clean and Jerk", "category": "olympic", "muscle_groups": ["full_body"], "equipment": "barbell"},
        {"name": "Snatch", "category": "olympic", "muscle_groups": ["full_body"], "equipment": "barbell"},
        {"name": "Power Clean", "category": "olympic", "muscle_groups": ["back", "hamstrings", "shoulders"], "equipment": "barbell"},
        {"name": "Hang Clean", "category": "olympic", "muscle_groups": ["back", "hamstrings", "shoulders"], "equipment": "barbell"},
        {"name": "Push Press", "category": "olympic", "muscle_groups": ["shoulders", "triceps", "core"], "equipment": "barbell"},
        {"name": "Clean Pull", "category": "olympic", "muscle_groups": ["back", "hamstrings"], "equipment": "barbell"},

        # FOREARMS
        {"name": "Wrist Curls", "category": "pull", "muscle_groups": ["forearms"], "equipment": "barbell"},
        {"name": "Reverse Wrist Curls", "category": "pull", "muscle_groups": ["forearms"], "equipment": "barbell"},
        {"name": "Farmer's Walk", "category": "pull", "muscle_groups": ["forearms", "core"], "equipment": "dumbbell"},
        {"name": "Plate Pinches", "category": "pull", "muscle_groups": ["forearms"], "equipment": "other"},
        {"name": "Dead Hangs", "category": "pull", "muscle_groups": ["forearms", "back"], "equipment": "bodyweight"},
    ]

    for ex_data in exercises:
        exercise = Exercise(
            name=ex_data["name"],
            category=ex_data["category"],
            muscle_groups=ex_data["muscle_groups"],
            equipment=ex_data["equipment"],
            is_custom=False
        )
        db.add(exercise)

    db.commit()
    db.close()
    print(f"Seeded {len(exercises)} exercises into database")


if __name__ == "__main__":
    seed_exercises()
