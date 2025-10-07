Prerequisites
Along with these instructions, you should have received a file containing utilities called utils.py.
Instructions
Your client is a deep-space transit company that specialises on voyages spanning beyond the three-year mark. For these extended interstellar “jumps”, human travelers are placed into stasis, a form of induced coma. To safeguard neurophysiological functions and ensure their well-being, the client has engaged our cerebral monitoring service for real-time alerts of neural anomalies and summaries of critical cognitive deviations. They have provided a high-level overview of the data streams and services they require for analysis.
This system involves a continuous stream of time series data from neural monitoring, which will be periodically retrieved and stored in an optimal data structure. Additionally, a prediction service will analyze this time series data to produce real-time binary outputs, accumulating every 15 seconds. This service should simulate a model that randomly assigns positive labels to clusters within the time series, aiming for approximately a 5% positive rate and assuming small data payloads for the model. Finally, a notification service needs to be implemented to accumulate these binary outputs every 5 minutes and send notifications to ground control.
Implement the back-end service
1. Data Ingestion
● Develop a feature to ingest data that comes from a mocked stream of data, as specified in the provided utils.py module. Ensure this ingestion mechanism is also usable by automated processes, serving as an effective push mechanism for independent systems orchestrating data flow.
● Demonstrate interaction with this component via a client.
2. Patient Registration
● Create an API to register new patients to the system.
● Consider any enhancements that might be required for the overall patient flow.
3. Patient Summary
● Develop an API to retrieve summaries of enrolled patients.
● Consider additional data or metadata that would be useful to track for patient summaries.
4. Patient Statistics
● Implement the computation of neural monitoring statistics* based on the data associated with each patient. You can use the predefined brain monitoring statistics in the utils.py.
● Consider how to orchestrate these computations in conjunction with a responsive front-end experience and how they interact with incoming data.
5. Utils.py
We provide functions that might help with understanding the Input/Output data format and statistics calculations / model calculations. Use as is, or amend according to your requirements. It is not important to focus on developing or amending these routines further.
● Use calculate_adr as a measure for patient statistics.
● Use model_binary_example as a mock for binary output for the same input. Raw_data represents the neural time series data that under this circumstance consist of 21 channels, sampled at 256Hz.
●
Submitting
We expect your submission to include:
○ An API that supports data upload (ingest) via other means than just the upload button.
○ Data model/storage.
○ API documentation.