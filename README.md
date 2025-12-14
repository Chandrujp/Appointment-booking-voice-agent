
# Doctor Appointment Booking Voice AI Agent (Breakpoint-25)

> **A Next-Gen Healthcare Booking System powered by Voice AI.**

This repository contains the **Doctor Booking Agent**, an AI-driven system that automates patient appointment confirmations and symptom checking.

## Key Features

- **WhatsApp Booking**: Seamless integration for booking appointments via WhatsApp.
- **Multilingual Support**: AI agent capable of conversing in multiple languages.
- **Smart Follow-ups**: Automated reminder calls scheduled 1 hour and 2 hours before appointments.



### Web Interface

| **Admin Dashboard** | **Doctor Dashboard** |
| :---: | :---: |
| <img src="https://github.com/sujitlaware1809/Breakpoint-25/blob/main/doctor_booking_agent/frontend/public/admin.jpg" width="100%" alt="Admin Dashboard" /> | <img src="doctor_booking_agent/frontend/public/dco2.jpg" width="100%" alt="Doctor Dashboard" /> |

| **Doctor Profile** | **Analytics View** |
| :---: | :---: |
| <img src="doctor_booking_agent/frontend/public/docter.png" width="100%" alt="Doctor Profile" /> | <img src="doctor_booking_agent/frontend/public/admin1.jpg" width="100%" alt="Analytics" /> |

### WhatsApp Integration

| **Appointment Confirmation** | **Follow-up Reminder** |
| :---: | :---: |
| <img src="doctor_booking_agent/frontend/public/appiountment_con.jpeg" width="200" alt="WhatsApp Confirmation" /> | <img src="doctor_booking_agent/frontend/public/appiotiment_followup.jpeg" width="200" alt="Follow-up Reminder" /> |

## Repository Structure

- **`doctor_booking_agent/`**: The main application code (Frontend + Backend + Agent Logic).
  - See [Application Documentation](doctor_booking_agent/README.md) for setup and usage.
- **`prompts/`**: Contains the system prompts and templates used by the AI.
  - `english.txt`: The base persona text.
  - `prompt.txt`: The active XML-based system prompt.
  - `evaluationTool.json`: The schema for call evaluation and data extraction.
- **`recordings/`**: Contains top 4 sample call recordings and token compression analysis.
- **`evaluationTool.json`**: Reference copy of the evaluation schema.
## System Architecture

```mermaid
graph TD
    User((Patient))
    Portal[Frontend Portal]
    API{Backend API}
    DB[(Database)]
    Agent[Voice AI Agent]
    Scheduler[Scheduler]
    WhatsApp[WhatsApp API]

    User -->|1. Books Appointment| Portal
    Portal -->|2. API Request| API
    API -->|3. Store Data| DB
    API -->|4. Trigger Confirmation| Agent
    Agent <-->|5. Voice Call| User
    Agent -->|6. Sync Result| API
    API -->|7. Send Confirmation| WhatsApp
    WhatsApp -->|8. Message| User
    
    Scheduler -->|9. Check Pending| DB
    Scheduler -->|10. 1hr Reminder| WhatsApp
    Scheduler -->|11. 2hr Reminder| Agent
```



## Quick Start

To run the full application (Frontend and Backend), navigate to the application folder:

```bash
cd doctor_booking_agent
# Follow instructions in doctor_booking_agent/README.md
```

## Configuration Reference

### Call Evaluation Schema
The agent uses a specific JSON schema to evaluate calls and extract booking details. See `prompts/evaluationTool.json` for the definition.

### Voice Activity Detection (VAD) Settings
The following VAD engines are supported for the voice agent:

| Engine    | Start   | End   | Character         | Use Case |
| --------- | ------- | ----- | ----------------- | -------- |
| **LOKEN**     | instant | 100ms | Responsive        | Testing, baseline, clean audio |
| **KAAN**      | 50ms    | 550ms | Aggressive        | Need fastest response, accept false triggers |
| **POLUX**     | 128ms   | 160ms | Balanced          | Noisy environment, need stability |
| **ANCHORITE** | 200ms   | 800ms | Patient           | Very conservative, minimize interruptions |
| **CALGAR**    | 50ms    | 400ms | Fast-in, slow-out | Good all-rounder for telephony |
| **VALDOR**    | 50ms    | 400ms | Fast-in, slow-out | **Production default** - best balance |
| **CAWL**      | 50ms    | 400ms | Fast-in, slow-out | Maximum performance, have native libs |

## Tools and Scripts

- **Makefile**: Contains commands to query the call server.
- **Postman Collection**: [View Documentation](https://documenter.getpostman.com/view/29008927/2sB3dSQUQE)
