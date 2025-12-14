# Output Directory

This directory contains call logs and session data from the Voice AI Receptionist system for doctor appointment bookings.

## Overview

Each JSON file in this directory represents a completed call session with detailed information about the conversation, AI interactions, and booking outcomes.

## File Naming

Files are named using the call ID from the database:
- Format: `{call_id}.json`
- Example: `258.json` corresponds to database record with `id: 258`

## JSON Structure

Each call log file contains the following top-level structure:

```json
{
  "data": { ... },
  "status": "success",
  "status_code": 200,
  "action_code": "DO_NOTHING"
}
```

### Data Object Fields

#### Call Metadata
- **id**: Database record ID
- **call_id**: Unique call identifier (UUID format)
- **created**: Timestamp when call was initiated
- **phone_number**: Customer's phone number
- **status**: Call status (e.g., "completed")
- **exotel_id**: Exotel call identifier

#### AI Configuration
- **prompt**: The complete AI master prompt containing:
  - Critical directives and constraints
  - Persona and tone settings
  - Vocal output constraints (12-word limit)
  - Hospital roster with doctor details
  - Step-by-step conversation instructions

- **evaluation_tool**: Tool configuration for capturing call outcomes:
  - Required fields: booked, name, symptoms, specialty
  - Optional fields: date, time

#### Call Details
The `call_details` object contains comprehensive session information:

##### Events Array
Chronological log of all call events:
- `call-initiated`: Call started
- `websocket-established`: Connection established
- `gemini-session-ready`: AI model ready
- `greeting-complete`: Initial greeting finished
- `idle-prompt-needed`: User inactive, prompt sent
- `tool-call`: AI invoked a function (end_call, call_outcomes, call_summary)
- `termination-requested`: Call ending initiated
- `evaluation-start/completed`: Post-call evaluation phase

##### Tool Calls
Record of all AI function invocations:
- `end_call`: Call termination with reason
- `call_outcomes`: Structured booking data capture
- `call_summary`: Natural language call summary

##### Phase History
State transitions during the call:
1. `initiated` → `connecting`
2. `connecting` → `active`
3. `active` → `evaluating`
4. `evaluating` → `terminated`

##### Usage Metadata
Token consumption statistics:
- Total tokens used
- Breakdown by modality (TEXT/AUDIO)

##### Call Outcomes Data
Structured booking information:
- Patient name
- Symptoms reported
- Specialty identified
- Appointment time
- Booking status (boolean)

##### Call Summary Data
Natural language summary of the conversation

##### Transcription Data
- **transcripts**: Array of conversation transcripts
- **interruptionTimestamps**: When user interrupted AI
- **turnCompleteTimestamps**: When conversation turns completed
- **generationCompleteTimestamps**: When AI generation finished

## Common Use Cases

### 1. Analyzing Call Success
Check `call_details.callOutcomesData.booked` to determine if appointment was booked successfully.

### 2. Extracting Booking Information
Access structured data from:
```json
data.call_details.callOutcomesData: {
  "name": "John Smith",
  "symptoms": "Bone pain",
  "specialty": "Orthopedics",
  "time": "10:00 AM",
  "booked": true
}
```

### 3. Reviewing Call Flow
Examine `events` array to understand conversation progression and identify bottlenecks.

### 4. Token Usage Tracking
Monitor `usageMetadata` for cost analysis and optimization.

### 5. Quality Assurance
Review:
- Call summaries for accuracy
- Phase transitions for proper flow
- Tool calls for correct AI behavior
- Interruption patterns for user experience

## Call Status Values

- **completed**: Call ended normally with booking
- **terminated**: Call ended without booking
- **failed**: Technical failure during call

## Termination Reasons

Common values in `call_details.terminationReason`:
- **Booked**: Appointment successfully booked
- **User hangup**: Customer ended call
- **No booking needed**: Informational call only
- **System error**: Technical issue

## Notes

- All timestamps are in Unix epoch milliseconds
- Phone numbers are in E.164 format (+91...)
- The system enforces a 12-word maximum per AI response
- Idle prompts trigger after ~40-50 seconds of inactivity
