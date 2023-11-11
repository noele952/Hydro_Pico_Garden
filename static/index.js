function selectOptionAndSubmit(option) {
  // Set the selected plant in the hidden input field
  document.getElementById("selected-plant").value = option;

  // Submit the form
  document.getElementById("start-form").submit();
}

function validateAndRedirect(event) {
  if (!selectedPlant) {
    alert("Please select a plant");
    event.preventDefault(); // Prevent the default form submission
    return false;
  }
  return true;
}

// updateData.js

function updateSensorData() {
  // Fetch updated sensor data from the server
  fetch("/sensorReadings")
    .then((response) => response.json())
    .then((data) => {
      // Update the HTML content with the new data
      document.getElementById("temperature").innerText =
        data.temperature + " F";
      document.getElementById("humidity").innerText = data.humidity + " %";
      document.getElementById("pressure").innerText = data.pressure + " hPa";
      document.getElementById("pico_temp").innerText = data.pico_temp;
      document.getElementById("water_temp").innerText = data.water_temp + " F";
      document.getElementById("light_percentage").innerText =
        data.light_percentage + " %";
    })
    .catch((error) => {
      console.error("Error fetching sensor data:", error);
    });
}

// Update sensor data every 5 seconds
setInterval(updateSensorData, 5000);
updateSensorData();

function updatePumpStatus() {
  // Fetch data from your route
  fetch("/gardenReadings") // Adjust the route accordingly
    .then((response) => response.json())
    .then((data) => {
      // Update waterpump status
      const waterpumpStatusItem = document.querySelector(
        ".pump-status-item:nth-child(1) .status"
      );
      if (data.waterpump_on === 1) {
        waterpumpStatusItem.innerHTML = "ON";
        waterpumpStatusItem.classList.add("status-true");
      } else {
        waterpumpStatusItem.innerHTML = "OFF";
        waterpumpStatusItem.classList.remove("status-true");
      }

      // Update airpump status
      const airpumpStatusItem = document.querySelector(
        ".pump-status-item:nth-child(2) .status"
      );
      if (data.airpump_on === 1) {
        airpumpStatusItem.innerHTML = "ON";
        airpumpStatusItem.classList.add("status-true");
      } else {
        airpumpStatusItem.innerHTML = "OFF";
        airpumpStatusItem.classList.remove("status-true");
      }

      // Update heater status
      const heaterStatusItem = document.querySelector(
        ".pump-status-item:nth-child(3) .status"
      );
      if (data.heater_on === 1) {
        heaterStatusItem.innerHTML = "ON";
        heaterStatusItem.classList.add("status-true");
      } else {
        heaterStatusItem.innerHTML = "OFF";
        heaterStatusItem.classList.remove("status-true");
      }
    })
    .catch((error) => console.error("Error fetching pump status:", error));
}

// Update pump status every 5 seconds
setInterval(updatePumpStatus, 5000); // Adjust the interval as needed

// Call updatePumpStatus once to initialize the status
updatePumpStatus();
