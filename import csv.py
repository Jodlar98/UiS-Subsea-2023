import csv
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime, timedelta

## Finn først ID fra mikrokontroller og sett som key
## Legg inn hvilken verdi en skal lese ut fra hvilke byte det er i skjemaet 
## Husk å legge inn .log fil i file path

def process_values(key, values):
    if key == '33':
        return ["Controller", *values]
    elif key == '130':
        return ["REG", float(values[0][1:]) / 100, "ESC", float(values[1]) / 100]
    elif key == '145':
        return ["KOM", float(".".join(values))]
    elif key == '150':
        return ["PW12_1_Current", float(values[0][1:]) / 1000, "PW12_1_Temp", float(values[1]) / 100]
    elif key == '151':
        return ["PW12_2_Current", float(values[0][1:]) / 1000, "PW12_2_Temp", float(values[1]) / 100]
    elif key == '152':
        return ["PW5", float(values[1]) / 100]
    elif key == '139':
        return ["Dybde", float(values[0][1:]), "Water", float(values[1]) / 100]
    else:
        return None

file_path = r"C:\Users\joard\OneDrive\Skrivebord\Subsea_data_log\2023-05-03 16.08.43 data.log"

with open(file_path, 'r') as f:
    input_text = f.read()

# Split input text into lines
lines = input_text.strip().split("\n")

data = []
interested_keys = ['33', '130', '145', '150', '151', '152', '139']
time_format = "%H:%M:%S,%f"

# Process each line
for line in lines:
    # Split line by whitespace
    parts = line.split()

    # Extract timestamp
    timestamp = datetime.strptime(parts[1], time_format)

    # Extract key and value
    key = parts[3].strip("':{")
    value_parts = parts[4:]

    # Check if the key is in the list of interested keys
    if key in interested_keys:
        # Combine the rest of the line into a single string and remove unwanted characters
        value_str = "".join(value_parts).strip("',}")
        value_list = value_str.split(',')

        processed_values = process_values(key, value_list)
        if len(processed_values) > 3:
            data.append([timestamp, processed_values[0], processed_values[1]])
            data.append([timestamp, processed_values[2], processed_values[3]])
        else:
            data.append([timestamp, *processed_values])

# Get the starting timestamp
start_time = data[0][0]

# Filter data to only include the first 20 minutes
filtered_data = [row for row in data if row[0] - start_time <= timedelta(minutes=50)]

# Write data to CSV file
with open('output.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['Timestamp', 'Name', 'Value'])
    csv_writer.writerows(filtered_data)

# Plotting the data
board_data = defaultdict(list)

for row in filtered_data:
    timestamp, board, value = row[0], row[1], row[2]
    board_data[board].append((timestamp, value))

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Define lists to store current and temperature measurements
current_measurements = ['PW12_1_Current', 'PW12_2_Current']
temperature_measurements = ['PW12_1_Temp', 'PW12_2_Temp', 'PW5', 'Dybde', 'Water', 'KOM', 'ESC', 'REG']

for board, time_data in board_data.items():
    timestamps, values = zip(*time_data)
    if board in current_measurements:
        ax1.plot(timestamps, values, label=board)
    elif board in temperature_measurements:
        ax2.plot(timestamps, values, label=board)

ax1.set_title('Current Measurements')
ax1.set_ylabel('Current (A)')
ax1.legend()

ax2.set_title('Temperature Measurements')
ax2.set_xlabel('Timestamp')
ax2.set_ylabel('Temperature (°C)')
ax2.legend()

plt.xticks(rotation=30)
plt.tight_layout()
plt.show()
import pandas as pd

data_list = []
for board, time_data in board_data.items():
    timestamps, values = zip(*time_data)
    for t, v in zip(timestamps, values):
        data_list.append({"Timestamp": t, "Board": board, "Value": v})

df = pd.DataFrame(data_list)
df.to_csv("output_data.csv", index=False)


