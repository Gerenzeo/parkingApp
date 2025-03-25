# ParkingApp

ParkingApp is an application built with FastAPI for managing parking spot rentals. It allows users to book parking spots, manage their statuses, and track rental times.

## Description

ParkingApp provides functionality for renting parking spots. The application includes a system for reserving parking spaces and an API for interacting with parking spot and rental data. This app is ideal for use in parking lots or garages where users can easily reserve a space in advance.

## Features

- **Reserve Parking Spots**: Users can book available parking spots through the API.
- **Track Rentals**: The system keeps track of rental times and statuses.
- **Manage Parking Spot Availability**: Admins can update parking spot statuses (available, reserved, occupied).
- **RESTful API**: Built using FastAPI, ensuring fast and efficient handling of requests.

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- SQLAlchemy (for database management)

## Installation

To install and run the project locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone <repository_url>
    ```
2. Navigate to the project directory:
    ```bash
    cd parkingAPP
    ```
3. Create a virtual environment:
    ```bash
    python -m venv venv
    ```
4. Activate the virtual environment:
    - On Windows:
        ```bash
        venv\Scripts\activate
        ```
    - On MacOS/Linux:
        ```bash
        source venv/bin/activate
        ```
5. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

To start the application, use Uvicorn to run FastAPI:

```bash
uvicorn main:app --reload
