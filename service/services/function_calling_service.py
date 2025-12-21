from typing import Literal
from datetime import date as date_
from services.rag_service import get_relevant_logs
from db.logs_repo import get_log_by_date as get_log_by_date_db
from db.goals_repo import list_goals

def get_user_specific_logs(user_id: str):
    def get_logs(query: str) -> list[str | None]:
        '''Gets relevant logs for the user based on the query via a RAG system
        
        Args:
            query: The natural language query to search for logs.
            
        Returns:
            A list of relevant logs.
        '''
        logs = get_relevant_logs(user_id=user_id, query=query)
        if not logs:
            return ["No logs found for the query: {query}"]

        return [f"{log.get('date', '')}: {log.get('content', '')}" for log in logs]
    
    return get_logs


def get_user_specific_log_by_date(user_id: str):
    def get_log_by_date(date: str) -> str:
        '''Gets a specific log for the user based on the date

        Args:
            date: The date of the log to retrieve in the format YYYY-MM-DD.

        Returns:
            The log content for the specified date.
        '''
        log = get_log_by_date_db(user_id=user_id, date=date_(year=int(date[:4]), month=int(date[5:7]), day=int(date[8:10])))
        if not log:
            return "No log found for the date: {date}"

        return f"{log.date}: {log.content}"
    
    return get_log_by_date

def get_user_specific_goals(user_id: str):
    def get_goals(status: Literal["all", "completed", "in_progress"]) -> list[str]:
        ''' Gets the goals for a user
        
        Args:
            status: The status of the goals to retrieve ("all", "completed", "in_progress").

        Returns:
            A list of goals.
        '''
        goals = list_goals(user_id=user_id, status=status).items
        if not goals:
            return ["No goals found for the user"]

        goals_list = []
        for i, goal in enumerate(goals):
            input_text = f"{i+1}. {goal.text}\n"
            input_text += f"Tags: {', '.join(goal.tags)}\n"
            goals_list.append(input_text)

        return goals_list

    return get_goals