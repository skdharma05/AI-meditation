import json
from my_crew.crew import MyCrew

def generate_custom_meditation(meditation_type='mindfulness', duration=8, difficulty='beginner', theme='relaxation', progress_callback=None):
    """
    Generate a custom meditation session with specific parameters, with progress reporting.
    """
    inputs = {
        'meditation_type': meditation_type,
        'duration': duration,
        'difficulty_level': difficulty,
        'theme': theme
    }
    try:
        crew = MyCrew().crew()
        if progress_callback:
            progress_callback('crew_initialized', 'Crew initialized')
        # Initialize agents
        for agent_name in ['meditation_script_generator', 'content_writer', 'timing_orchestrator', 'json_formatter']:
            if progress_callback:
                progress_callback('agent_initialized', f"Agent '{agent_name}' initialized")
        # Initialize tasks
        for task_name in ['meditation_design_task', 'content_creation_task', 'timing_orchestration_task', 'json_generation_task']:
            if progress_callback:
                progress_callback('task_initialized', f"Task '{task_name}' initialized")
        if progress_callback:
            progress_callback('kickoff', 'Crew kickoff started')
        result = crew.kickoff(inputs=inputs)
        if progress_callback:
            progress_callback('completed', 'Crew execution completed')
        # --- Post-process: always return a dict ---
        if isinstance(result, str):
            cleaned = result.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            cleaned = cleaned.strip()
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            cleaned = cleaned.strip()
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            try:
                result = json.loads(cleaned)
            except Exception as e:
                if progress_callback:
                    progress_callback('failed', f'Invalid JSON output: {e}')
                raise Exception(f"CrewAI output is not valid JSON: {e}\nRaw output: {cleaned}")
        print(f"Custom {meditation_type} meditation ({duration} min) generated successfully!")
        return result
    except Exception as e:
        if progress_callback:
            progress_callback('failed', str(e))
        raise Exception(f"An error occurred while generating custom meditation: {e}")


