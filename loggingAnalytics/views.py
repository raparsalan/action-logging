# analyticsApp/views.py

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import json 
from datetime import datetime, timedelta

from .utils import get_mongo_collection, get_user_category, OLD_USER_IDS, NEW_USER_IDS,PAGE_ACTIONS 

class AnalyticsView(APIView):
    def get(self, request,id=None):
        collection, client = get_mongo_collection()
        start_date = None
        end_date = None

        if id == 1:
            # siklus 1 
            start_date = datetime(2025, 6, 13, 0, 0, 0) # 9 Juni 2025
            end_date = datetime(2025, 6, 19, 23, 59, 59) # 13 Juni 2025
        elif id == 2:
            # siklus 2
            start_date = datetime(2025, 6, 21, 0, 0, 0) # 21 Juni 2025 
            end_date = datetime(2025, 6, 27, 23, 59, 59) # 27 Juni 2025
        
        try:
            query_filter = {}
            if start_date and end_date:
                # Pastikan format tanggal di MongoDB Anda sesuai untuk perbandingan
                query_filter["log_created"] = {"$gte": start_date, "$lte": end_date}
            
            all_logs_data = list(collection.find(query_filter)) 
            print(f"AnalyticsView: Fetched {len(all_logs_data)} raw logs from MongoDB.")
            
            unique_new_users = set() 
            unique_old_users = set() 
            
            new_users_successful_bookings = 0
            old_users_successful_bookings = 0 
            
            new_users_total_sessions = 0
            old_users_total_sessions = 0 

            new_session_durations = [] 
            old_session_durations = [] 
            
            raw_session_lengths_new = []
            raw_session_lengths_old = []

            feature_access_new = {} 
            feature_access_old = {}

            filter_counts_new = {}
            filter_counts_old = {}

            daily_activity_new = {} 
            daily_activity_old = {} 

            hourly_activity_new = {} 
            hourly_activity_old = {} 

            first_action_after_login_new = {} 
            first_action_after_login_old = {} 

            last_action_new = {} 
            last_action_old = {} 

            search_trend_new = {} 
            search_trend_old = {} 
            
            search_keyword_frequency_new = {}
            search_keyword_frequency_old = {}

            # --- Loop melalui setiap log untuk analisis detail ---
            for log_index, log_doc in enumerate(all_logs_data):
                id_user = log_doc.get('id_user')
                user_category = get_user_category(id_user,id) 
                
                log_created_dt = None
                raw_log_created = log_doc.get('log_created')
                try:
                    if isinstance(raw_log_created, dict) and '$date' in raw_log_created:
                        log_created_dt = datetime.fromtimestamp(raw_log_created['$date'] / 1000)
                    elif isinstance(raw_log_created, str):
                        log_created_dt = datetime.fromisoformat(raw_log_created)
                    elif isinstance(raw_log_created, datetime):
                        log_created_dt = raw_log_created
                except (ValueError, TypeError) as e:
                    print(f"Error parsing log_created for log {log_doc.get('idLog')}: {raw_log_created} - {e}")
                    log_created_dt = None 

                list_action_raw = log_doc.get('list_action', '[]')
                list_action = [] 

                # get list action
                if isinstance(list_action_raw, str):
                    try:
                        list_action = json.loads(list_action_raw)
                    except json.JSONDecodeError as e:
                        print(f"Error JSON decoding list_action for log {log_doc.get('idLog')}: {list_action_raw[:100]}... - {e}")
                elif isinstance(list_action_raw, list): 
                    list_action = list_action_raw

                if not list_action: continue

                # calculate session length 
                session_length = len(list_action)
                if user_category == 'new_user': raw_session_lengths_new.append(session_length)
                elif user_category == 'old_user': raw_session_lengths_old.append(session_length)

                # calculate total users
                if id_user:
                    if user_category == 'new_user': unique_new_users.add(id_user)
                    elif user_category == 'old_user': unique_old_users.add(id_user) 

                # calculate total session
                if user_category == 'new_user': new_users_total_sessions += 1
                elif user_category == 'old_user': old_users_total_sessions += 1 

                if log_created_dt:
                    date_key = log_created_dt.strftime("%Y-%m-%d")
                    hour_key = log_created_dt.strftime("%H") 
                    
                    if user_category == 'new_user':
                        daily_activity_new[date_key] = daily_activity_new.get(date_key, 0) + 1
                        hourly_activity_new[hour_key] = hourly_activity_new.get(hour_key, 0) + 1
                    elif user_category == 'old_user': 
                        daily_activity_old[date_key] = daily_activity_old.get(date_key, 0) + 1
                        hourly_activity_old[hour_key] = hourly_activity_old.get(hour_key, 0) + 1

                first_action_time_in_session = None
                last_action_time_in_session = None
                
                is_booking_successful = False
                
                first_action_id_after_login_in_session = None 

                # get first action after login
                if len(list_action) >= 2 and list_action[0].get('id_action') == 'login':
                    if len(list_action) >= 3 and list_action[1].get('id_action') == 'home_page':
                        first_action_id_after_login_in_session = list_action[2].get('id_action')
                    elif len(list_action) == 2 and list_action[1].get('id_action') == 'home_page':
                        first_action_id_after_login_in_session = 'home_page' 

                # looping for list action
                for idx, action in enumerate(list_action):
                    action_id = action.get('id_action')
                    action_time_str = action.get('time_action')

                    if action_id == 'submit_booking':
                        is_booking_successful = True

                    try:
                        action_time = datetime.fromisoformat(action_time_str)
                        if first_action_time_in_session is None or action_time < first_action_time_in_session:
                            first_action_time_in_session = action_time
                        if last_action_time_in_session is None or action_time > last_action_time_in_session:
                            last_action_time_in_session = action_time
                    except (ValueError, TypeError) as e:
                        print(f"Error parsing action_time for log {log_doc.get('idLog')}, action '{action_id}': {action_time_str} - {e}")
                        action_time = None 

                    # calculate feature access
                    if action_id and action_id in PAGE_ACTIONS:
                        if user_category == 'new_user': feature_access_new[action_id] = feature_access_new.get(action_id, 0) + 1
                        elif user_category == 'old_user': feature_access_old[action_id] = feature_access_old.get(action_id, 0) + 1 
                    
                    if action_id and action_id.startswith('search:') and action_time: 
                        search_dt_key = action_time.strftime("%Y-%m-%d %H") 
                        if user_category == 'new_user': search_trend_new[search_dt_key] = search_trend_new.get(search_dt_key, 0) + 1
                        elif user_category == 'old_user': search_trend_old[search_dt_key] = search_trend_old.get(search_dt_key, 0) + 1 
                    
                    # calculate search trend
                    if action_id and action_id.startswith('search:'):
                        keyword = action_id.split(':', 1)[1].strip() 
                        if keyword: 
                            if user_category == 'new_user':
                                search_keyword_frequency_new[keyword] = search_keyword_frequency_new.get(keyword, 0) + 1
                            elif user_category == 'old_user':
                                search_keyword_frequency_old[keyword] = search_keyword_frequency_old.get(keyword, 0) + 1

                    if action_id and action_id.startswith('filter_'):
                        if user_category == 'new_user':
                            filter_counts_new[action_id] = filter_counts_new.get(action_id, 0) + 1
                        elif user_category == 'old_user':
                            filter_counts_old[action_id] = filter_counts_old.get(action_id, 0) + 1

                if is_booking_successful:
                    if user_category == 'new_user': new_users_successful_bookings += 1
                    elif user_category == 'old_user': old_users_successful_bookings += 1 
                
                if first_action_time_in_session and last_action_time_in_session:
                    session_duration_seconds = (last_action_time_in_session - first_action_time_in_session).total_seconds()
                    if user_category == 'new_user': new_session_durations.append(session_duration_seconds)
                    elif user_category == 'old_user': old_session_durations.append(session_duration_seconds) 

                if first_action_id_after_login_in_session:
                    if user_category == 'new_user':
                        first_action_after_login_new[first_action_id_after_login_in_session] = first_action_after_login_new.get(first_action_id_after_login_in_session, 0) + 1
                    elif user_category == 'old_user': 
                        first_action_after_login_old[first_action_id_after_login_in_session] = first_action_after_login_old.get(first_action_id_after_login_in_session, 0) + 1 

                if list_action: 
                    last_action_id_in_session = list_action[-1].get('id_action')
                    if last_action_id_in_session:
                        if user_category == 'new_user':
                            last_action_new[last_action_id_in_session] = last_action_new.get(last_action_id_in_session, 0) + 1
                        elif user_category == 'old_user': 
                            last_action_old[last_action_id_in_session] = last_action_old.get(last_action_id_in_session, 0) + 1 

            avg_session_duration_new = sum(new_session_durations) / len(new_session_durations) if new_session_durations else 0
            avg_session_duration_old = sum(old_session_durations) / len(old_session_durations) if old_session_durations else 0 
            
            def get_top_n_items(counts_dict, n=5):
                """Helper untuk mendapatkan top N item dari dictionary berdasarkan count."""
                sorted_items = sorted(counts_dict.items(), key=lambda item: item[1], reverse=True)
                return sorted_items[:n] # Mengembalikan list of (item, count) tuples

            top_5_filters_new = get_top_n_items(filter_counts_new, 5)
            top_5_filters_old = get_top_n_items(filter_counts_old, 5)

            response_data = {
                "totalNewUsers": len(unique_new_users),
                "totalOldUsers": len(unique_old_users), 
                "newUsersTotalSessions": new_users_total_sessions,
                "oldUsersTotalSessions": old_users_total_sessions, 
                "newUsersSuccessfulBookings": new_users_successful_bookings,
                "oldUsersSuccessfulBookings": old_users_successful_bookings, 
                "avgSessionDurationNew": round(avg_session_duration_new), 
                "avgSessionDurationOld": round(avg_session_duration_old), 
                "featureAccessNew": feature_access_new,
                "featureAccessOld": feature_access_old, 
                "top5FiltersNew": top_5_filters_new,
                "top5FiltersOld": top_5_filters_old,
                "featureAccessOld": feature_access_old, 
                "dailyActivityNew": daily_activity_new,
                "dailyActivityOld": daily_activity_old, 
                "hourlyActivityNew": hourly_activity_new,
                "hourlyActivityOld": hourly_activity_old, 
                "firstActionAfterLoginNew": first_action_after_login_new,
                "firstActionAfterLoginOld": first_action_after_login_old, 
                "lastActionNew": last_action_new, 
                "lastActionOld": last_action_old, 
                "rawSessionDurationsNew": new_session_durations, 
                "rawSessionDurationsOld": old_session_durations, 
                "rawSessionLengthsNew": raw_session_lengths_new,
                "rawSessionLengthsOld": raw_session_lengths_old,
                "searchTrendNew": search_trend_new, 
                "searchTrendOld": search_trend_old, 
                "searchKeywordFrequencyNew": search_keyword_frequency_new,
                "searchKeywordFrequencyOld": search_keyword_frequency_old,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error during analytics data processing: {e}")
            return Response({"error": "Failed to retrieve analytics data", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if client:
                client.close()