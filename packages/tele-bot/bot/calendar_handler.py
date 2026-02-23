import EventKit
from Foundation import NSDate, NSTimeZone

class CalendarHandler():
    def add_event_native(self, title, start_dt, duration_minutes, calendar_type:str = None, source_name:str = 'iCloud', alert_minutes_before:str = None):
        store = EventKit.EKEventStore.alloc().init()
        
        # Request for permission
        permission_determined = False

        def request_callback(granted, error):
            nonlocal permission_determined
            permission_determined = True
            if granted:
                print("\n✅ SUCCESS: Permission Granted! You can now run your main script.")
            else:
                print("\n❌ DENIED: You clicked 'Don't Allow'. You must fix this in System Settings.")
        
        status = EventKit.EKEventStore.authorizationStatusForEntityType_(EventKit.EKEntityTypeEvent)
        
        if status == 0:
            print("Status: Not Determined. Attempting to trigger popup...")
            
            if hasattr(store, "requestFullAccessToEventsWithCompletion_"):
                store.requestFullAccessToEventsWithCompletion_(request_callback)
            else:
                store.requestAccessToEntityType_completion_(EventKit.EKEntityTypeEvent, request_callback)

            # Wait up to 30 seconds for interaction
            counter = 0
            while not permission_determined and counter < 60:
                time.sleep(0.5)
                counter += 1
                
        elif status == 1: # Restricted
            print("Status: Restricted (Parental controls or MDM profile blocking access).")
            return
        elif status == 2: # Denied
            print("Status: Denied. You previously clicked 'Don't Allow'. Run 'tccutil reset Calendar' in terminal.")
            return
        elif status == 3: # Authorized
            print("Status: Authorized. You already have access!")



        event = EventKit.EKEvent.eventWithEventStore_(store)
        event.setTitle_(title)
        event.setLocation_("Singapore")

        if calendar_type:
            # Get all available calendars for events
            all_calendars = store.calendarsForEntityType_(EventKit.EKEntityTypeEvent)
            target_cal = None

            # Search for a match (case-insensitive)
            for cal in all_calendars:
                # Get the names of the Calendar and its Source (Account)
                c_name = cal.title()
                s_name = cal.source().title()
                
                # Check for match (case-insensitive)
                if c_name.lower() == calendar_type.lower() and s_name.lower() == source_name.lower():
                    target_cal = cal
                    break
            
            if target_cal:
                print(f"📅 Using calendar: {target_cal.title()}")
                event.setCalendar_(target_cal)
            else:
                print(f"⚠️ Warning: Calendar '{calendar_type}' not found. Using default.")
                event.setCalendar_(store.defaultCalendarForNewEvents())
        else:
            print(f"📅 Using default calendar")
            event.setCalendar_(store.defaultCalendarForNewEvents())
        
        if alert_minutes_before is not None:
            offset_seconds = -1 * (alert_minutes_before * 60)
            alarm = EventKit.EKAlarm.alarmWithRelativeOffset_(offset_seconds)
            event.addAlarm_(alarm)
            print(f"🔔 Alert set for {alert_minutes_before} minutes before.")

        if start_dt.tzinfo is None:
            sgt = ZoneInfo("Asia/Singapore")
            start_dt = start_dt.replace(tzinfo=sgt)
            
        timestamp = start_dt.timestamp()
        
        # Create NSDate (Absolute time)
        ns_start = NSDate.dateWithTimeIntervalSince1970_(timestamp)
        ns_end = NSDate.dateWithTimeIntervalSince1970_(timestamp + (duration_minutes * 60))
        
        event.setStartDate_(ns_start)
        event.setEndDate_(ns_end)
        
        # Explicitly set the event metadata to Singapore Time
        sg_tz = NSTimeZone.timeZoneWithName_("Asia/Singapore")
        event.setTimeZone_(sg_tz)
        
        # 5. Save the Event
        result, error = store.saveEvent_span_commit_error_(event, 0, True, None)

        if result:
            print(f"✅ Success: '{title}' added for {start_dt.strftime('%d %b %H:%M')} SGT")
        else:
            print(f"❌ Error saving event: {error}")

calendar_handler = CalendarHandler()