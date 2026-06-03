# Telegram and Fediverse Event Name Updater

## What does this do?
This little tool updates your Telegram last name and/or Fediverse display name based on an iCal URL with events that you plan on attending.
You can configure a cutoff, i.e. how many days events may be in the future at most to be included. The default setting is 6 months.
You can also specify whether you want to show only the next upcoming event or a list of events, per service.

If you choose to show a list of events, the tool will format your last name like this:
* If you're attending EVENT1 right now and EVENT2 and EVENT3 are in the future: `@ EVENT1 → EVENT2, EVENT3`
* If you're attending EVENT1 right now and no other events are in the future: `@ EVENT1`
* If you're not attending any event right now and EVENT1 and EVENT2 are in the future: `→ EVENT1, EVENT2`
* If you're attending EVENT1 and EVENT2 right now (how?) and EVENT3 is in the future: `@ EVENT1, EVENT2 → EVENT3`
* If you're not attending any event and no event is in the future, the last name will be blank.

If you choose to show only the next event, it will format according to the same rules, but only ever show one event.

## What do I need?
For Telegram, you will need a Telegram API ID and API Hash (this is different from a Telegram Bot), which you can get [here](https://core.telegram.org/api/obtaining_api_id).
On first run, the script will ask you for your Telegram phone number to log in.

For the Fediverse, the tool will prompt you to authorize it.

You need to rename `secrets.example.py` to `secrets.py` and add your secrets before running the script as well as rename `settings.example.py` to `settings.py` and change the settings if necessary.

You should set up the script to run regularly, ideally once per hour, via a cronjob.

## How do I add events?
The script will check all events in the specified iCal calendar for the special tags `tg-name` and `tg-name-active` (for Telegram) and `fedi-name` and `fedi-name-active` (for the Fediverse)in the event's description.
So if you want to include an event in your Telegram or Fediverse name, just add one line to the event description like `tg-name: ABC` or `fedi-name: ABC`.
Optionally, you can also add another line like `tg-name-active: XYZ` or `fedi-name-active: XYZ` to set a different name for the event once it starts.
This will cause the event to show up as "ABC" in the list of upcoming events in your name and as "XYZ" once it starts, no matter what the event is actually called.
If no `-name-active` tag is found, the `-name` tag will be used as both the upcoming and current event name.
If a `-name-active` tag is found but no `-name` tag, the event will only show up once it's active.