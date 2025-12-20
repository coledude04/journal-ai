from services.rag_service import get_relevant_logs

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