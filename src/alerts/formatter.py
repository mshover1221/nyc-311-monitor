def format_alert_text(triggered_conditions):
    messages = []

    for condition in triggered_conditions:
        message = (
            f"{condition['borough']} — {condition['category']}\n"
            f"{condition['start_time']} – {condition['end_time']}\n"
            f"{condition['current_count']} complaints\n"
            f"Historical threshold: {condition['threshold']}\n"
            f"Based on {condition['historical_count']} comparable periods"
        )
        messages.append(message)
    
    return "\n\n".join(messages)