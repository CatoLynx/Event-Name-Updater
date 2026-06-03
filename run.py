"""
Telegram and Fediverse Event Name Updater
Copyright (C) 2024-2026 Julian Metzler

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import datetime
import requests

from dateutil import parser
from ics import Calendar

from secrets import *
from settings import *

if USE_TG:
    import asyncio
    from pyrogram import Client
    from pyrogram.raw import functions

if USE_FEDI:
    import os
    from mastodon import Mastodon


def get_events():
    cal = Calendar(requests.get(ICAL_URL).text)
    events = list(cal.timeline)
    return events


def get_event_short_name(event, platform):
    """
    Gets a short name for an event based on the description field.
    """
    
    if event.description is None:
        return (None, None)
    pre_name = None
    active_name = None
    desc_lines = event.description.splitlines()
    for line in desc_lines:
        if line.startswith(f"{platform}-name:"):
            pre_name = line.lstrip(f"{platform}-name:").strip()
        if line.startswith(f"{platform}-name-active:"):
            active_name = line.lstrip(f"{platform}-name-active:").strip()
    return (pre_name, active_name)


def generate_event_tags(events, platform, lookahead_days, single, add_space):
    """
    Generates the display name suffix.
    
    events:         List of events in the calendar
    platform:       A string that will be used to filter events from the calendar.
                    Example: 'tg' will only consider events that have a "tg-name"
                    entry in the event description.
    lookahead_days: Number of days to look into the future
    single:         If True, only the first upcoming event will be added.
                    If False, a comma separated list will be generated.
    add_space:      If True, add a space before the arrow or @
    """
    
    current = []
    future = []
    now = datetime.datetime.now().astimezone()
    
    for event in events:
        delta = event.begin - now
        # Add current event(s)
        if (event.begin <= now <= event.end):
            pre_name, active_name = get_event_short_name(event, platform)
            if active_name:
                current.append(active_name)
            elif pre_name:
                current.append(pre_name)
        # Skip events in the past
        elif (now >= event.end):
            continue
        # Skip events too far in the future
        elif (delta.days > lookahead_days):
            continue
        # Add future event(s)
        else:
            pre_name, active_name = get_event_short_name(event, platform)
            if pre_name:
                future.append(pre_name)
    
    if single:
        current = current[:1]
        if current:
            future = []
        else:
            future = future[:1]
    
    suffix = ""
    if current:
        if add_space:
            suffix += " "
        suffix += "@ " + ", ".join(current)
    if future:
        if current or add_space:
            suffix += " "
        suffix += "→ " + ", ".join(future)
    return suffix


async def update_name_tg(suffix):
    app = Client("event_name_update", api_id=TG_API_ID, api_hash=TG_API_HASH)
    async with app:
        await app.invoke(functions.account.UpdateProfile(last_name=suffix))


def update_name_fedi(suffix):
    if not os.path.exists(".fedi-client-secret"):
        Mastodon.create_app(FEDI_APP_NAME, api_base_url=FEDI_URL, to_file=".fedi-client-secret")
    
    if not os.path.exists(".fedi-user-secret"):
        fedi = Mastodon(client_id=".fedi-client-secret")
        print("Open this URL to log in:", fedi.auth_request_url())
        fedi.log_in(code=input("Enter auth code: "), to_file=".fedi-user-secret")
    
    fedi = Mastodon(access_token=".fedi-user-secret")
    me = fedi.me()
    current_name = me.display_name
    
    # Get the base name from the display name. This might be flaky...
    base_name = current_name.replace(FEDI_DEFAULT_SUFFIX, "").split(" →")[0].split(" @")[0]
    print("            Base name:", base_name)
    
    name = base_name + suffix
    fedi.account_update_credentials(display_name=name)


def main():
    events = get_events()
    
    if USE_TG:
        tg_suffix = generate_event_tags(events, platform="tg", lookahead_days=TG_EVENT_LOOKAHEAD_DAYS, single=TG_SINGLE_MODE, add_space=False)
        if not tg_suffix:
            tg_suffix = TG_DEFAULT_SUFFIX
        print("[Telegram]  Updating suffix:", tg_suffix)
        asyncio.run(update_name_tg(tg_suffix))
    
    if USE_FEDI:
        fedi_suffix = generate_event_tags(events, platform="fedi", lookahead_days=FEDI_EVENT_LOOKAHEAD_DAYS, single=FEDI_SINGLE_MODE, add_space=True)
        if not fedi_suffix:
            fedi_suffix = FEDI_DEFAULT_SUFFIX
        print("[Fediverse] Updating suffix:", fedi_suffix)
        update_name_fedi(fedi_suffix)


if __name__ == "__main__":
    main()
