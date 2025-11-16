"""
Database migration utilities to handle schema updates
"""
from sqlalchemy import inspect, text
from database import engine


def migrate_database():
    """Apply schema migrations to add new columns"""
    inspector = inspect(engine)

    # Get existing columns for each table
    users_columns = [col['name'] for col in inspector.get_columns('users')] if 'users' in inspector.get_table_names() else []
    workout_exercises_columns = [col['name'] for col in inspector.get_columns('workout_exercises')] if 'workout_exercises' in inspector.get_table_names() else []
    workout_sets_columns = [col['name'] for col in inspector.get_columns('workout_sets')] if 'workout_sets' in inspector.get_table_names() else []

    with engine.connect() as conn:
        # Add weight_unit to users table
        if 'users' in inspector.get_table_names() and 'weight_unit' not in users_columns:
            print("Adding weight_unit column to users table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN weight_unit VARCHAR(10) DEFAULT 'kg'"))
            conn.commit()

        # Add phase to workout_exercises table
        if 'workout_exercises' in inspector.get_table_names() and 'phase' not in workout_exercises_columns:
            print("Adding phase column to workout_exercises table...")
            conn.execute(text("ALTER TABLE workout_exercises ADD COLUMN phase VARCHAR(20) DEFAULT 'main'"))
            conn.commit()

        # Add is_completed to workout_sets table
        if 'workout_sets' in inspector.get_table_names() and 'is_completed' not in workout_sets_columns:
            print("Adding is_completed column to workout_sets table...")
            conn.execute(text("ALTER TABLE workout_sets ADD COLUMN is_completed BOOLEAN DEFAULT 0"))
            conn.commit()

    print("Database migration completed successfully")


if __name__ == "__main__":
    migrate_database()
