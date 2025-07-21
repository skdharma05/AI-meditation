"""
Custom tools for meditation session generation
"""

from crewai.tools import BaseTool
from typing import Dict, Any, Optional, Union
import json
from enum import Enum
from med_crew.models import (
    SpeakParameters, PauseParameters, BreathCueParameters, 
    BreathingCycleParameters, SilenceParameters, MusicParameters, ActionParameters
)


class ActionType(str, Enum):
    # VoiceAgent actions
    speak = "speak"
    pause = "pause"

    # BreathAgent actions
    inhale_cue = "inhale_cue"
    exhale_cue = "exhale_cue"
    breathing_cycle = "breathing_cycle"

    # TimerAgent actions
    silence = "silence"
    transition_cue = "transition_cue"
    segment_timer = "segment_timer"

    # MusicAgent actions
    play = "play"
    fade_in = "fade_in"
    fade_out = "fade_out"
    volume_change = "volume_change"


class ActionParameterGeneratorTool(BaseTool):
    name: str = "Action Parameter Generator"
    description: str = "Generates appropriate parameters for different action types in a meditation session"

    def _run(
        self,
        action_type: str,
        segment_type: str,
        content_info: Optional[Dict[str, Any]] = None,
    ) -> Union[SpeakParameters, PauseParameters, BreathCueParameters, 
                      BreathingCycleParameters, SilenceParameters, MusicParameters]:
        """
        Generate parameters for an action based on its type and context

        Args:
            action_type: The type of action (speak, breathing_cycle, etc.)
            segment_type: The type of segment (opening, breathwork, etc.)
            content_info: Optional content information to use for generating parameters

        Returns:
            A properly typed parameter object for the action type
        """
        # Default content for different segment types if not provided
        default_content = {
            "opening": {
                "voice_texts": [
                    "Welcome to this inner peace meditation.",
                    "Find a comfortable position and allow yourself to settle.",
                    "Take a deep breath in, and slowly exhale.",
                    "Let's begin our practice together.",
                ],
                "breath_cues": {
                    "inhale": "Breathe in deeply",
                    "exhale": "Release and let go",
                },
            },
            "breathwork": {
                "voice_texts": [
                    "Bring your attention to your breath.",
                    "Notice the natural rhythm of your breathing.",
                    "Allow your breath to deepen naturally.",
                    "With each breath, release any tension you may be holding.",
                ],
                "breath_cues": {
                    "inhale": "Inhale deeply through your nose",
                    "exhale": "Exhale completely through your mouth",
                },
            },
            "closing": {
                "voice_texts": [
                    "Begin to deepen your breath.",
                    "Gently wiggle your fingers and toes.",
                    "When you're ready, slowly open your eyes.",
                    "Carry this peace with you throughout your day.",
                ]
            },
        }

        # Use provided content or fall back to defaults
        segment_content = content_info.get(segment_type, {}) if content_info else {}
        voice_texts = segment_content.get(
            "voice_texts",
            default_content.get(segment_type, default_content["opening"]).get(
                "voice_texts", []
            ),
        )
        breath_cues = segment_content.get(
            "breath_cues",
            default_content.get(segment_type, default_content["opening"]).get(
                "breath_cues", {}
            ),
        )

        # Generate parameters based on action type
        if action_type == ActionType.speak:
            # Get a text or use default
            text = voice_texts[0] if voice_texts else "Take a moment to be present."
            return SpeakParameters(text=text)
            
        elif action_type == ActionType.pause:
            return PauseParameters(reason="Allow for reflection")
            
        elif action_type == ActionType.inhale_cue:
            return BreathCueParameters(
                phase="inhale",
                text=breath_cues.get("inhale", "Breathe in")
            )
            
        elif action_type == ActionType.exhale_cue:
            return BreathCueParameters(
                phase="exhale",
                text=breath_cues.get("exhale", "Breathe out")
            )
            
        elif action_type == ActionType.breathing_cycle:
            return BreathingCycleParameters(
                inhale_seconds=4,
                hold_seconds=0,
                exhale_seconds=6,
                rest_seconds=2,
                repetitions=3,
                inhale_cue=breath_cues.get("inhale", "Breathe in"),
                exhale_cue=breath_cues.get("exhale", "Breathe out")
            )
            
        elif action_type == ActionType.silence:
            return SilenceParameters(type="reflection")
            
        elif action_type == ActionType.transition_cue:
            # Use SpeakParameters for transition since we don't have a specific class
            return SpeakParameters(text="Transitioning")
            
        elif action_type in [
            ActionType.play,
            ActionType.fade_in,
            ActionType.fade_out,
            ActionType.volume_change,
        ]:
            return MusicParameters(track_id="ambient_peace", volume=0.3)
        
        # Default to empty SpeakParameters if action type not recognized
        return SpeakParameters(text="Placeholder instruction")


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
        timing_plan = {"total_duration": total_seconds, "segments": []}

        # Calculate segment timing
        current_time = 0
        for i, segment in enumerate(segments):
            segment_duration = segment.get("duration", 60)  # default 1 minute
            timing_plan["segments"].append(
                {
                    "name": segment.get("name", f"Segment {i + 1}"),
                    "start_time": current_time,
                    "end_time": current_time + segment_duration,
                    "duration": segment_duration,
                }
            )
            current_time += segment_duration

        return timing_plan


class BreathingPatternTool(BaseTool):
    name: str = "Breathing Pattern Generator"
    description: str = (
        "Generates breathing patterns for different meditation techniques"
    )

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
            "calm": {"inhale": 3, "hold": 0, "exhale": 5, "pause": 2},
        }

        pattern = patterns.get(pattern_type, patterns["natural"])
        cycle_duration = sum(pattern.values())
        cycles = duration // cycle_duration

        return {
            "pattern": pattern,
            "cycles": cycles,
            "total_duration": cycles * cycle_duration,
            "instructions": f"Repeat {cycles} times: Inhale {pattern['inhale']}s, Hold {pattern['hold']}s, Exhale {pattern['exhale']}s, Pause {pattern['pause']}s",
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
                "advanced": "Welcome to this practice. Begin by establishing your intention for this session.",
            },
            "closing": {
                "beginner": "Slowly bring your awareness back. Wiggle your fingers and toes. Open your eyes when ready.",
                "intermediate": "Begin to transition back, carrying this sense of calm with you.",
                "advanced": "Integrate this awareness as you return to your daily activities.",
            },
        }

        return {
            "opening": content_templates["opening"].get(
                difficulty, content_templates["opening"]["beginner"]
            ),
            "closing": content_templates["closing"].get(
                difficulty, content_templates["closing"]["beginner"]
            ),
            "theme": theme,
            "type": meditation_type,
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

            validation_result = {"valid": True, "errors": []}

            for field in required_fields:
                if field not in data:
                    validation_result["valid"] = False
                    validation_result["errors"].append(
                        f"Missing required field: {field}"
                    )

            if "session" in data:
                for field in session_fields:
                    if field not in data["session"]:
                        validation_result["valid"] = False
                        validation_result["errors"].append(
                            f"Missing session field: {field}"
                        )

            return validation_result

        except json.JSONDecodeError as e:
            return {"valid": False, "errors": [f"Invalid JSON: {str(e)}"]}
