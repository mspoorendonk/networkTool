# Description of features

## Audible network state (Tone)
### Purpose
A tone can be played to help the user sense the networks state without looking at the screen. The frequency of the tone indicates the state. This allows the user to walk around with the laptop to find dead spots or to tweak the network settings without having to constantly check the screen.

### Details
The tone can be tied to a specific timeseries in the settings pane. It can also be set to 'muted' there.

The tone will be high for low latency or high bandwith.

The timeseries that the tone can be attached to are:
- ping1
- pingFirstHop
- iperfUp
- iperfDown
- ooklaUp
- ooklaDown

The maximum frequency must be reached when the bandwidth reaches the maximum.

### Testing
No separate tests will be written for this feature. It will be tested as part of the overall network testing. The existing testcases that test the network settings will be extended to cover the sound feature.