# Meditation AI Architecture

## Overview

This meditation AI system uses CrewAI to generate structured meditation sessions that can be executed by specialized agents in a React Native frontend application.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Native Frontend                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Meditation    │  │   Session       │  │   Real-time     │ │
│  │   Player UI     │  │   Controls      │  │   Execution     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                │ JSON Meditation Sessions
                                │
┌─────────────────────────────────────────────────────────────┐
│                    CrewAI Backend System                    │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                Generation Crew                          │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐ │ │
│  │  │   Meditation  │  │    Content    │  │    Timing     │ │ │
│  │  │    Script     │  │    Writer     │  │ Orchestrator  │ │ │
│  │  │   Generator   │  │     Agent     │  │     Agent     │ │ │
│  │  └───────────────┘  └───────────────┘  └───────────────┘ │ │
│  │                           │                             │ │
│  │                           ▼                             │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │              JSON Formatter Agent                   │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Execution Agents                        │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐ │ │
│  │  │     Voice     │  │    Breath     │  │     Timer     │ │ │
│  │  │     Agent     │  │     Agent     │  │     Agent     │ │ │
│  │  └───────────────┘  └───────────────┘  └───────────────┘ │ │
│  │                           │                             │ │
│  │  ┌─────────────────────────┴─────────────────────────────┐ │ │
│  │  │                 Music Agent                          │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## CrewAI Agent Specifications

### Generation Crew Agents

#### 1. Meditation Script Generator Agent
- **Role**: Meditation Script Architect
- **Responsibility**: Design overall meditation structure, flow, and therapeutic progression
- **Output**: High-level meditation plan with segments and timing

#### 2. Content Writer Agent
- **Role**: Mindful Content Creator
- **Responsibility**: Write all voice scripts, instructions, and guided content
- **Output**: Complete voice scripts for each meditation segment

#### 3. Timing Orchestrator Agent
- **Role**: Meditation Timing Specialist
- **Responsibility**: Calculate precise timing for all elements
- **Output**: Exact timing specifications for voice, breath, silence, and music

#### 4. JSON Formatter Agent
- **Role**: Meditation Data Architect
- **Responsibility**: Convert meditation plan into executable JSON format
- **Output**: Complete JSON meditation session file

### Execution Agents (Frontend Integration)

#### 1. Voice Agent
- **Actions**: speak, pause, fade
- **Parameters**: text, duration, volume, voice_type
- **Integration**: Text-to-speech engine in React Native

#### 2. Breath Agent
- **Actions**: inhale_cue, exhale_cue, breathing_cycle
- **Parameters**: inhaleTime, exhaleTime, pauseTime, repetitions, tone
- **Integration**: Audio cues and visual breathing guides

#### 3. Timer Agent
- **Actions**: silence, transition_cue, segment_timer
- **Parameters**: silenceDuration, cue_type, countdown
- **Integration**: Silent periods and transition management

#### 4. Music Agent
- **Actions**: play, fade_in, fade_out, volume_change
- **Parameters**: musicTrack, volume, fade_duration
- **Integration**: Background audio management

## JSON Schema Structure

The generated meditation sessions follow this structure:

```json
{
  "session": {
    "title": "Session Title",
    "duration": 480,
    "theme": "clarity and peace",
    "difficulty": "beginner",
    "segments": [
      {
        "id": "segment_id",
        "name": "Segment Name",
        "startTime": 0,
        "endTime": 60,
        "duration": 60,
        "actions": [
          {
            "agent": "voice|breath|timer|music",
            "action": "specific_action",
            "timing": {
              "start": 0,
              "duration": 10
            },
            "parameters": {
              // Agent-specific parameters
            }
          }
        ]
      }
    ]
  }
}
```

## Frontend Architecture (React Native)

### Core Components

#### 1. Meditation Player
```javascript
// Main player component that interprets JSON and coordinates agents
<MeditationPlayer 
  sessionData={meditationJSON}
  onComplete={handleComplete}
  onPause={handlePause}
/>
```

#### 2. Agent Controllers
```javascript
// Voice Agent Controller
const VoiceController = {
  speak: (text, duration) => TextToSpeech.speak(text),
  pause: (duration) => new Promise(resolve => setTimeout(resolve, duration * 1000))
}

// Breath Agent Controller  
const BreathController = {
  breathingCycle: (params) => {
    // Visual breathing guide + audio cues
    showBreathingAnimation(params.inhaleTime, params.exhaleTime);
    playBreathingTones(params.tone);
  }
}

// Timer Agent Controller
const TimerController = {
  silence: (duration) => new Promise(resolve => setTimeout(resolve, duration * 1000)),
  transitionCue: (tone) => playTransitionSound(tone)
}

// Music Agent Controller
const MusicController = {
  play: (track, volume) => AudioManager.play(track, volume),
  fadeIn: (duration, targetVolume) => AudioManager.fadeIn(duration, targetVolume),
  fadeOut: (duration) => AudioManager.fadeOut(duration)
}
```

#### 3. Session Executor
```javascript
class SessionExecutor {
  constructor(sessionData) {
    this.session = sessionData.session;
    this.currentTime = 0;
    this.isPlaying = false;
  }

  async start() {
    this.isPlaying = true;
    for (const segment of this.session.segments) {
      if (!this.isPlaying) break;
      await this.executeSegment(segment);
    }
  }

  async executeSegment(segment) {
    const promises = segment.actions.map(action => {
      return new Promise(resolve => {
        setTimeout(() => {
          this.executeAction(action);
          resolve();
        }, action.timing.start * 1000);
      });
    });
    
    await Promise.all(promises);
  }

  executeAction(action) {
    const controller = this.getAgentController(action.agent);
    controller[action.action](action.parameters);
  }
}
```

## How to Run the Current System

### 1. Install Dependencies
```bash
cd /home/amirth/Work/GD003/cw_ai/my_crew
uv sync
```

### 2. Generate a Meditation Session
```bash
# Using CrewAI CLI
crewai run

# Or using the Python script directly
uv run python src/my_crew/main.py
```

### 3. Custom Meditation Generation
```python
from src.my_crew.main import generate_custom_meditation

# Generate different types of meditations
generate_custom_meditation(
    meditation_type='loving-kindness',
    duration=10,
    difficulty='intermediate', 
    theme='compassion and self-love'
)
```

## Next Steps for Implementation

### 1. Backend API Layer
- Create FastAPI server to expose meditation generation endpoints
- Add authentication and user preference management
- Implement caching for generated sessions

### 2. React Native Frontend
- Set up audio management (react-native-sound or expo-av)
- Implement text-to-speech integration
- Create breathing animation components
- Build meditation player UI

### 3. Enhanced Features
- User preference learning
- Session customization
- Progress tracking
- Offline session storage

### 4. Testing and Refinement
- A/B testing different meditation styles
- User feedback integration
- Performance optimization
- Voice quality enhancement

## File Structure

```
my_crew/
├── src/my_crew/
│   ├── config/
│   │   ├── agents.yaml          # Agent configurations
│   │   └── tasks.yaml           # Task definitions
│   ├── tools/
│   │   ├── meditation_tools.py  # Custom tools for meditation
│   │   └── custom_tool.py       # Default tools
│   ├── crew.py                  # Main crew definition
│   └── main.py                  # Entry point and utilities
├── meditation_schema.json        # JSON schema for sessions
├── example_meditation_session.json  # Example output
└── ARCHITECTURE.md              # This file
```

This architecture provides a solid foundation for building a sophisticated AI-powered meditation application using CrewAI's multi-agent capabilities.
