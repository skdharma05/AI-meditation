from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from enum import Enum

"""
Base Enums
"""

class AgentType(str, Enum):
    voice = "VoiceAgent"
    breath = "BreathAgent"
    timer = "TimerAgent"
    music = "MusicAgent"

class ActionType(str, Enum):
    speak = "speak"
    pause = "pause"
    fade = "fade"
    inhale_cue = "inhale_cue"
    exhale_cue = "exhale_cue"
    breathing_cycle = "breathing_cycle"
    silence = "silence"
    transition_cue = "transition_cue"
    segment_timer = "segment_timer"
    play = "play"
    fade_in = "fade_in"
    fade_out = "fade_out"
    volume_change = "volume_change"

class SegmentType(str, Enum):
    opening = "opening"
    breathwork = "breathwork"
    body_awareness = "body_awareness"
    visualization = "visualization"
    silence = "silence"
    affirmation = "affirmation"
    closing = "closing"
    custom = "custom"

"""
Task 1: Meditation Design Models
"""

class MeditationStructure(BaseModel):
    """Initial meditation session structure and flow"""
    title: str = Field(..., description="Title of the meditation session")
    theme: str = Field(..., description="Main theme of the meditation")
    difficulty: str = Field(..., description="Difficulty level (beginner, intermediate, advanced)")
    total_duration_minutes: int = Field(..., ge=1, description="Total duration in minutes")
    background_music_style: Optional[str] = Field(None, description="Suggested music style if any")
    planned_segments: List[Dict[str, Any]] = Field(..., description="Outline of planned segments with approximate timing")
    key_elements: List[str] = Field(..., description="Important elements to include in the meditation")
    breathing_pattern: Dict[str, Any] = Field(..., description="Recommended breathing pattern")

    class Config:
        schema_extra = {
            "example": {
                "title": "Clarity and Peace Meditation",
                "theme": "Finding inner clarity and peaceful awareness",
                "difficulty": "beginner",
                "total_duration_minutes": 8,
                "background_music_style": "Gentle ambient tones, minimal melody",
                "planned_segments": [
                    {"name": "Opening", "duration_seconds": 30, "type": "opening"},
                    {"name": "Breathwork", "duration_seconds": 60, "type": "breathwork"},
                    {"name": "Body Scan", "duration_seconds": 90, "type": "body_awareness"},
                    {"name": "Guided Visualization", "duration_seconds": 120, "type": "visualization"},
                    {"name": "Silent Meditation", "duration_seconds": 60, "type": "silence"},
                    {"name": "Affirmations", "duration_seconds": 60, "type": "affirmation"},
                    {"name": "Closing", "duration_seconds": 60, "type": "closing"}
                ],
                "key_elements": ["Body awareness", "Breathing focus", "Clarity visualization", "Peace affirmations"],
                "breathing_pattern": {"inhale": 4, "hold": 2, "exhale": 6, "rest": 2}
            }
        }

"""
Task 2: Content Creation Models
"""

class ScriptSegment(BaseModel):
    """Detailed script for a meditation segment"""
    segment_title: str = Field(..., description="Title of this segment")
    segment_type: SegmentType = Field(..., description="Type of meditation segment")
    timing_description: str = Field(..., description="Timing description (e.g., '00:00-01:30')")
    voice_instructions: List[str] = Field(..., description="List of voice instructions to read")
    breath_guidance: Optional[Dict[str, Any]] = Field(None, description="Breath guidance if applicable")
    silence_periods: Optional[List[Dict[str, Any]]] = Field(None, description="Silence periods if applicable")

class MeditationContent(BaseModel):
    """Complete content for a meditation session"""
    title: str = Field(..., description="Title of the meditation session")
    segments: List[ScriptSegment] = Field(..., description="List of all meditation script segments")
    
"""
Task 3: Timing Orchestration Models
"""

class TimedInstruction(BaseModel):
    """A single timed instruction in the meditation"""
    agent: AgentType = Field(..., description="Agent responsible for this instruction")
    instruction_type: ActionType = Field(..., description="Type of instruction")
    start_time_seconds: int = Field(..., ge=0, description="Start time in seconds")
    duration_seconds: int = Field(..., ge=0, description="Duration in seconds")
    content: Optional[str] = Field(None, description="Content of instruction (e.g., voice text)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional parameters")

class TimedSegment(BaseModel):
    """A segment with precisely timed instructions"""
    segment_title: str = Field(..., description="Title of this segment")
    segment_type: SegmentType = Field(..., description="Type of meditation segment")
    start_time_seconds: int = Field(..., ge=0, description="Start time in seconds")
    end_time_seconds: int = Field(..., ge=1, description="End time in seconds")
    instructions: List[TimedInstruction] = Field(..., description="Timed instructions within this segment")

class MeditationTiming(BaseModel):
    """Complete timing for all meditation elements"""
    title: str = Field(..., description="Title of the meditation session")
    total_duration_seconds: int = Field(..., ge=1, description="Total duration in seconds")
    segments: List[TimedSegment] = Field(..., description="All timed segments")

    @validator('total_duration_seconds')
    def check_duration_matches_segments(cls, v, values):
        """Validate that total duration matches the end time of the last segment"""
        if 'segments' in values and values['segments']:
            segments = values['segments']
            max_end_time = max(segment.end_time_seconds for segment in segments)
            if v != max_end_time:
                raise ValueError(f"Total duration ({v}s) does not match end of last segment ({max_end_time}s)")
        return v

"""
Task 4: Final Meditation Session Model
"""

class Action(BaseModel):
    """An action performed by an agent during a meditation segment."""
    agent: AgentType = Field(..., description="The agent responsible for the action.")
    type: ActionType = Field(..., description="The type of action performed.")
    start_time_seconds: int = Field(..., ge=0, description="Start time of the action in seconds.")
    duration_seconds: int = Field(..., ge=1, description="Duration of the action in seconds.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters for the action.")

class Segment(BaseModel):
    """A segment of the meditation session, such as opening, breathwork, etc."""
    segment_title: str = Field(..., description="Title of the segment.")
    start_time_seconds: int = Field(..., ge=0, description="Start time of the segment in seconds.")
    end_time_seconds: int = Field(..., ge=1, description="End time of the segment in seconds.")
    actions: List[Action] = Field(..., description="List of actions in this segment.")

class MeditationSession(BaseModel):
    """The complete meditation session, including all segments and metadata."""
    title: str = Field(..., description="Title of the meditation session.")
    duration_seconds: int = Field(..., ge=1, description="Total duration of the session in seconds.")
    theme: str = Field(..., description="Theme of the meditation session.")
    difficulty: str = Field(..., description="Difficulty level (e.g., beginner, intermediate, advanced).")
    background_music_suggestion: str = Field(..., description="Suggested background music for the session.")
    segments: List[Segment] = Field(..., description="List of segments in the session.")

    class Config:
        schema_extra = {
            "example": {
                "title": "Clarity and Peace Meditation",
                "duration_seconds": 480,
                "theme": "Finding inner clarity and peaceful awareness",
                "difficulty": "beginner",
                "background_music_suggestion": "Soft ambient tones with minimal melody",
                "segments": [
                    {
                        "segment_title": "Opening and Preparation",
                        "start_time_seconds": 0,
                        "end_time_seconds": 30,
                        "actions": [
                            {
                                "agent": "VoiceAgent",
                                "type": "speak",
                                "start_time_seconds": 0,
                                "duration_seconds": 20,
                                "parameters": {
                                    "text": "Welcome to this meditation for clarity and peace. Find a comfortable position and gently close your eyes."
                                }
                            },
                            {
                                "agent": "MusicAgent",
                                "type": "fade_in",
                                "start_time_seconds": 0,
                                "duration_seconds": 10,
                                "parameters": {
                                    "target_volume": 0.2,
                                    "music_id": "ambient_calm"
                                }
                            }
                        ]
                    }
                ]
            }
        }
