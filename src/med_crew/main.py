from med_crew.crew import MyCrew
from med_crew.models import MeditationSession


def generate_custom_meditation(
    meditation_type: str = "mindfulness",
    duration: int = 8,
    difficulty: str = "beginner",
    theme: str = "clarity and peace",
) -> MeditationSession:
    from med_crew.tools.meditation_tools import ActionParameterGeneratorTool
    import time
    import sys

    # Track performance
    start_time = time.time()
    print(f"Starting meditation generation with type={meditation_type}, duration={duration}, difficulty={difficulty}")
    
    try:
        crew = MyCrew().crew()
        input_dict = {
            "meditation_type": meditation_type,
            "duration": duration,
            "difficulty_level": difficulty,
            "theme": theme,
        }
        
        # Execute the crew tasks
        print("Starting CrewAI execution...")
        result = crew.kickoff(input_dict)
        print("CrewAI execution completed successfully!")
        
        crew_finish_time = time.time()
        crew_execution_time = crew_finish_time - start_time
        print(f"Crew execution time: {crew_execution_time:.2f} seconds")
        
    except Exception as e:
        print(f"Error during crew execution: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc(file=sys.stdout)
        raise
    
    # Start tracking post-processing time
    post_processing_start = time.time()
    print("Starting parameter validation and post-processing...")

    try:
        # Create the parameter generator tool for validation once
        param_generator = ActionParameterGeneratorTool()
        
        # Create parameter maps to avoid regenerating the same parameters
        # This caches parameters by action_type and segment_type
        parameter_cache = {}
        
        # Get the session from the crew result
        print("Extracting meditation session from result...")
        meditation_session = result.pydantic
        
        # Process all segments in one pass - with optimized approach
        segment_count = len(meditation_session.segments)
        print(f"Processing {segment_count} segments...")
        
        for i, segment in enumerate(meditation_session.segments):
            segment_type = segment.type.value
            print(f"Processing segment {i+1}/{segment_count}: {segment.title} (type: {segment_type})")
            
            action_count = len(segment.actions)
            # Process all actions in this segment
            for j, action in enumerate(segment.actions):
                action_type = action.type.value
                
                # Create cache key for this combination
                cache_key = f"{action_type}_{segment_type}"
                
                try:
                    # Check if parameters exist and are valid
                    if (
                        not hasattr(action.parameters, "__dict__")
                        or not action.parameters.__dict__
                    ):
                        # Check cache first before generating new parameters
                        if cache_key in parameter_cache:
                            action.parameters = parameter_cache[cache_key]
                        else:
                            # Generate parameters and cache them
                            action.parameters = param_generator._run(
                                action_type=action_type, segment_type=segment_type
                            )
                            parameter_cache[cache_key] = action.parameters
                except Exception as e:
                    print(f"  Error in action {j+1}/{action_count} ({action_type}): {str(e)}")
                    # Generate parameters only if needed
                    if cache_key in parameter_cache:
                        action.parameters = parameter_cache[cache_key]
                    else:
                        action.parameters = param_generator._run(
                            action_type=action_type, segment_type=segment_type
                        )
                        parameter_cache[cache_key] = action.parameters
        
        print("Parameter post-processing completed successfully.")
        
    except Exception as e:
        print(f"Error during post-processing: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc(file=sys.stdout)
        raise
        
    finally:
        # Record post-processing time
        post_processing_end = time.time()
        post_processing_time = post_processing_end - post_processing_start
        print(f"Post-processing time: {post_processing_time:.2f} seconds")
        print(f"Percentage of post-processing: {(post_processing_time/(post_processing_time + crew_execution_time))*100:.1f}%")
        
        # Report total time
        total_time = time.time() - start_time
        print(f"Total execution time: {total_time:.2f} seconds")

    return meditation_session


if __name__ == "__main__":
    import time
    
    start_time = time.time()
    
    # Example usage
    meditation_session = generate_custom_meditation(
        meditation_type="mindfulness",
        duration=2,
        difficulty="intermediate",
        theme="inner peace",
    )
    
    # Calculate performance metrics
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n===== PERFORMANCE METRICS =====")
    print(f"Total execution time: {total_time:.2f} seconds")
    
    # Show a summary of the meditation session
    print(f"\nGenerated Meditation Session: {meditation_session}")

    # Display parameters for all actions in the first segment
    if meditation_session.segments:
        print(
            f"\nParameters for actions in the first segment '{meditation_session.segments[0].title}':"
        )
        for i, action in enumerate(meditation_session.segments[0].actions):
            print(f"  Action {i + 1}: {action.agent.value} - {action.type.value}")
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
