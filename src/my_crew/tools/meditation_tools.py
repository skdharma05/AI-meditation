"""
Custom tools for meditation session generation
"""

from crewai_tools import BaseTool
from typing import Dict, Any
import json

class MeditationTimingTool(BaseTool):
    name: str = "Meditation Timing Calculator"
    description: str = "Calculates precise timing for meditation segments, breathing patterns, and transitions"
    
    def _run(self, total_duration: int, segments: list) -> Dict[str, Any]:
        """
        Calculate timing for meditation segments
        
        Args:
            total_duration: Total meditation duration in minutes
            segments: List of segment names and relative durations
        """
        total_seconds = total_duration * 60
        timing_plan = {
            "total_duration": total_seconds,
            "segments": []
        }
        
        # Calculate segment timing
        current_time = 0
        for i, segment in enumerate(segments):
            segment_duration = segment.get('duration', 60)  # default 1 minute
            timing_plan["segments"].append({
                "name": segment.get('name', f'Segment {i+1}'),
                "start_time": current_time,
                "end_time": current_time + segment_duration,
                "duration": segment_duration
            })
            current_time += segment_duration
            
        return timing_plan


class BreathingPatternTool(BaseTool):
    name: str = "Breathing Pattern Generator"
    description: str = "Generates breathing patterns for different meditation techniques"
    
    def _run(self, pattern_type: str, duration: int) -> Dict[str, Any]:
        """
        Generate breathing patterns
        
        Args:
            pattern_type: Type of breathing (e.g., '4-7-8', 'box', 'natural')
            duration: Duration in seconds for the breathing exercise
        """
        patterns = {
            "4-7-8": {"inhale": 4, "hold": 7, "exhale": 8, "pause": 2},
            "box": {"inhale": 4, "hold": 4, "exhale": 4, "pause": 4},
            "natural": {"inhale": 4, "hold": 0, "exhale": 6, "pause": 2},
            "calm": {"inhale": 3, "hold": 0, "exhale": 5, "pause": 2}
        }
        
        pattern = patterns.get(pattern_type, patterns["natural"])
        cycle_duration = sum(pattern.values())
        cycles = duration // cycle_duration
        
        return {
            "pattern": pattern,
            "cycles": cycles,
            "total_duration": cycles * cycle_duration,
            "instructions": f"Repeat {cycles} times: Inhale {pattern['inhale']}s, Hold {pattern['hold']}s, Exhale {pattern['exhale']}s, Pause {pattern['pause']}s"
        }


class MeditationContentTool(BaseTool):
    name: str = "Meditation Content Generator"
    description: str = "Generates meditation content templates and voice scripts"
    
    def _run(self, meditation_type: str, theme: str, difficulty: str) -> Dict[str, Any]:
        """
        Generate meditation content templates
        
        Args:
            meditation_type: Type of meditation (mindfulness, loving-kindness, etc.)
            theme: Theme of the session (clarity, peace, etc.)
            difficulty: Difficulty level (beginner, intermediate, advanced)
        """
        content_templates = {
            "opening": {
                "beginner": "Welcome to this peaceful meditation. Find a comfortable position and allow yourself to settle.",
                "intermediate": "Welcome. Take a moment to arrive fully in this space, releasing the outside world.",
                "advanced": "Welcome to this practice. Begin by establishing your intention for this session."
            },
            "closing": {
                "beginner": "Slowly bring your awareness back. Wiggle your fingers and toes. Open your eyes when ready.",
                "intermediate": "Begin to transition back, carrying this sense of calm with you.",
                "advanced": "Integrate this awareness as you return to your daily activities."
            }
        }
        
        return {
            "opening": content_templates["opening"].get(difficulty, content_templates["opening"]["beginner"]),
            "closing": content_templates["closing"].get(difficulty, content_templates["closing"]["beginner"]),
            "theme": theme,
            "type": meditation_type
        }


class JSONValidationTool(BaseTool):
    name: str = "JSON Schema Validator"
    description: str = "Validates meditation session JSON against the required schema"
    
    def _run(self, meditation_json: str) -> Dict[str, Any]:
        """
        Validate meditation session JSON
        
        Args:
            meditation_json: JSON string to validate
        """
        try:
            data = json.loads(meditation_json)
            
            # Basic validation
            required_fields = ["session"]
            session_fields = ["title", "duration", "segments"]
            
            validation_result = {
                "valid": True,
                "errors": []
            }
            
            for field in required_fields:
                if field not in data:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Missing required field: {field}")
            
            if "session" in data:
                for field in session_fields:
                    if field not in data["session"]:
                        validation_result["valid"] = False
                        validation_result["errors"].append(f"Missing session field: {field}")
            
            return validation_result
            
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "errors": [f"Invalid JSON: {str(e)}"]
            }
