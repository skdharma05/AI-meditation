from med_crew.crew import MyCrew
from med_crew.models import MeditationSession

def generate_custom_meditation(
    meditation_type: str = "mindfulness",
    duration: int = 8,
    difficulty: str = "beginner",
    theme: str = "clarity and peace"
) -> MeditationSession:
    from med_crew.tools.meditation_tools import ActionParameterGeneratorTool
    
    crew = MyCrew().crew()
    input_dict = {
        "meditation_type": meditation_type,
        "duration": duration,
        "difficulty_level": difficulty,
        "theme": theme
    }
    result = crew.kickoff(input_dict)

    print(f"Result from crew: {result.pydantic}")
    
    # Create the parameter generator tool for validation
    param_generator = ActionParameterGeneratorTool()
    
    # Check if any action has parameters that need to be generated
    meditation_session = result.pydantic
    for segment in meditation_session.segments:
        for action in segment.actions:
            try:
                # Check if the parameter object is missing or empty
                # This will raise an exception if required fields are missing
                if not hasattr(action.parameters, '__dict__') or not action.parameters.__dict__:
                    # Generate appropriate parameters
                    action.parameters = param_generator._run(
                        action_type=action.type.value, 
                        segment_type=segment.type.value
                    )
            except Exception as e:
                print(f"Fixing parameters for action {action.type}: {str(e)}")
                action.parameters = param_generator._run(
                    action_type=action.type.value, 
                    segment_type=segment.type.value
                )
    
    return meditation_session


if __name__ == "__main__":
    # Example usage
    meditation_session = generate_custom_meditation(
        meditation_type="mindfulness",
        duration=2,
        difficulty="intermediate",
        theme="inner peace"
    )

    # Show a summary of the meditation session
    print(f"\nGenerated Meditation Session: {meditation_session}")
    
    # Display parameters for all actions in the first segment
    if meditation_session.segments:
        print(f"\nParameters for actions in the first segment '{meditation_session.segments[0].title}':")
        for i, action in enumerate(meditation_session.segments[0].actions):
            print(f"  Action {i+1}: {action.agent.value} - {action.type.value}")
            print(f"    Parameters: {action.parameters}")
            print("")
            
    # Count total actions and verify all have parameters
    total_actions = sum(len(segment.actions) for segment in meditation_session.segments)
    actions_with_params = sum(
        sum(1 for action in segment.actions if action.parameters) 
        for segment in meditation_session.segments
    )
    print(f"\nActions with parameters: {actions_with_params}/{total_actions}")
    
    if actions_with_params < total_actions:
        print("WARNING: Some actions still have empty parameters!")
    else:
        print("SUCCESS: All actions have parameters!")
