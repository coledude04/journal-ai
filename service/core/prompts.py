from models.logs import DailyLog
from models.goals import Goal

LLM_SYSTEM_INSTRUCTIONS = (
    "You are an assistant designed to give helpful and valuable feedback on a user's log of their day.\n"
    "You will be given the user's log of their day, some of their most recent logs, and their goals. Use these to generate valuable feedback.\n"
    "Note: This is standalone feedback and isn't a conversation, so please provide all the feedback you think is necessary in one message.\n\n"
    "You have access to the following tools:\n"
    "1. `get_logs` - This function retrieves a list of past logs from the user. Pass a simple natural language query and the function will return a list of relevant logs. "
    "Use this tool to find relevant logs that can help you provide more context and personalized feedback.\n"
)

def generate_input(current_log: DailyLog, prev_logs: list[DailyLog], goals: list[Goal]) -> str:
    input_text = f"New Log:\nDate: {current_log.date}\n{current_log.content}\n\n"
    input_text += "Previous Logs:\n"

    for i, log in enumerate(prev_logs):
        input_text += f"{i+1}. {log.date}: {log.content}\n\n"

    input_text += "Goals:\n"
    for i, goal in enumerate(goals):
        input_text += f"{i+1}. {goal.text}\n"
        input_text += f"Tags: {', '.join(goal.tags)}\n"

    return input_text