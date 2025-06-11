# Network Tool

### Overview

Network Tool is a comprehensive application designed to measure network speed and performance between hosts in a Local Area Network (LAN). The tool includes features such as running an iperf server, performing ping tests, and more. This README provides essential information on setting up, running, and using the application.

### Features

- **Iperf Server**: Runs an iperf server to measure network speed between two hosts in the LAN.
- **Ping Tests**: Performs ping tests to measure latency and packet loss.
- **Graphical Visualization**: Provides graphical visualization of network statistics using PyQtGraph.
- **Background Polling**: Monitors network interfaces and SSID changes in the background.
- **Data Export**: Allows exporting network statistics to CSV files.


<img src="resources/doc/networktool_ping.gif" />
<i>Measure ping latency to first hop and to google Meet video server</i>

<img src="resources/doc/networktool_ookla_alternating.gif" />
<i>Measure alternating up/download from Ookla</i>

### Installation

#### Prerequisites

- Python 3.12 or higher
- Inno Setup (for creating Windows installers)

#### Steps

1. **Clone the Repository**:
   ```sh
   git clone <repository_url>
   ```

2. **Install Dependencies**:
   ```sh
   poetry install
   ```

3. **Build the Application**:
   ```sh
   pyinstaller networktool.spec
   ```

4. **Create Windows Installer** (Optional):
   run the 
   ```sh
   package.bat
   ```

### Usage

#### Running the Application

To run the application, execute the following command:
```sh
python src/main.py
```

#### Using the Iperf Server

Measure network speed between two hosts in the LAN:

1. Start the iperf server on another machine in the LAN from the windows menu or by running ```iperf -s```.
2. Use the 'Start Iperf' feature in the application to measure network speed.

### License

This project is licensed under the GPL-3.0 License. See the `LICENSE` file for more details.

### Contact

For any questions or issues, please contact [Marc Spoorendonk](mailto:marc@spoorendonk.com).
