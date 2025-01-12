# Garmin Connect Yearly Elevation Gain

This Garmin Connect integration allows you to see your yearly elevation gain progress. It creates two sensors:

- Elevation Gain This Year
  - The accumulated elevation gain for the current year summed up for all activities.
- Days Ahead/Behind Target
  - The days that you are behind/ahead of the 100.000m target for the year.

NOTE: This integration doesn't support 2FA on Garmin Connect yet (support is coming), so if you have enabled it -and want to keep it- this integration doesn't work, it will try to login repeatedly and generate lots of 2FA codes via email.
The change of adding support for it is unlikely since the Garmin Connect API is closed source, and will not be open for open-sourced projects.

## Installation

### HACS - Recommended

- Have [HACS](https://hacs.xyz) installed, this will allow you to easily manage and track updates.
- Inside HACS click 'Explore & download repositories'
- Search for 'Garmin Connect'.
- Click on found integration.
- Click Download this repository with HACS.
- Restart Home-Assistant.
- Follow configuration steps below.

### Manual

- Copy directory `custom_components/garmin_connect` to your `<config dir>/custom_components` directory.
- Restart Home-Assistant.
- Follow configuration steps below.

## Configuration

Adding Garmin Connect to your Home Assistant instance can be done via the integrations user interface.

- Browse to your Home Assistant instance.
- In the sidebar click on Configuration.
- From the configuration menu select: Integrations.
- In the bottom right, click on the Add Integration button.
- From the list, search and select “Garmin Connect”.
- Follow the instruction on screen to complete the set up

After successful set up a standard set of sensors are enabled. You can enable more if needed by using the Integrations page.

Please be aware that Garmin Connect has very low rate limits, max. once every ~5 minutes.
