from my_crew.crew import MyCrew
from my_crew.models import MeditationSession

def generate_custom_meditation(
    meditation_type: str = "mindfulness",
    duration: int = 8,
    difficulty: str = "beginner",
    theme: str = "clarity and peace"
) -> MeditationSession:
    crew = MyCrew().crew()
    input_dict = {
        "meditation_type": meditation_type,
        "duration": duration,
        "difficulty_level": difficulty,
        "theme": theme
    }
    result  = crew.kickoff(input_dict)

    print(f"Result from crew: {result.pydantic}")

    result_dict = result.pydantic.model_dump()

    return MeditationSession(**result_dict)


if __name__ == "__main__":
    # Example usage
    meditation_session = generate_custom_meditation(
        meditation_type="mindfulness",
        duration=2,
        difficulty="intermediate",
        theme="inner peace"
    )

    print(f"Generated Meditation Session: {meditation_session}")
