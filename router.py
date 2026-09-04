import json
import os

from dotenv import load_dotenv
from openai import OpenAI


# --------------------------------------------------
# ENVIRONMENT
# --------------------------------------------------

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# --------------------------------------------------
# VALID STRATEGIES
# --------------------------------------------------

VALID_STRATEGIES = [
    "structured_rag",
    "graph_rag",
    "live_rag"
]


# --------------------------------------------------
# ROUTE QUESTION
# --------------------------------------------------

def route_question(question):

    q = question.lower().strip()

    # ==================================================
    # STEP 1: LIVE RAG
    # ==================================================

    weather_keywords = [
        "weather",
        "temperature",
        "forecast",
        "rain",
        "humidity",
        "wind"
    ]

    if any(word in q for word in weather_keywords):

        locations = [
            "bangalore",
            "hyderabad",
            "vijayawada",
            "chennai",
            "mumbai",
            "delhi",
            "pune",
            "chilakaluripet"
        ]

        city = None

        for location in locations:
            if location in q:
                city = location.title()
                break

        return {
            "strategy": "live_rag",
            "city": city
        }


    # ==================================================
    # STEP 2: GRAPH RAG
    # ==================================================
    # ONLY relationship questions go here.

    graph_keywords = [
        "manager",
        "reports to",
        "reporting",
        "relationship",
        "works with",
        "connected to"
    ]

    if any(word in q for word in graph_keywords):

        prompt = f"""
You are an employee relationship router.

The user's question requires Graph RAG.

Return ONLY valid JSON.

{{
    "strategy": "graph_rag",
    "employee_name": null
}}

Extract the employee name from the question.

USER QUESTION:
{question}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        content = response.choices[0].message.content

        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            raise ValueError(
                f"Router returned invalid JSON: {content}"
            )

        result["strategy"] = "graph_rag"

        return result


    # ==================================================
    # STEP 3: STRUCTURED RAG
    # ==================================================
    # Simple employee-data questions ALWAYS go here.

    structured_keywords = [
        "employee",
        "employees",
        "names",
        "list",
        "absent",
        "active",
        "inactive",
        "department",
        "location",
        "salary",
        "status",
        "count",
        "how many"
    ]

    if any(word in q for word in structured_keywords):

        location = None
        status = None
        department = None
        employee_id = None


        # ----------------------------------------------
        # LOCATION
        # ----------------------------------------------

        locations = [
            "bangalore",
            "hyderabad",
            "vijayawada",
            "chennai",
            "mumbai",
            "delhi",
            "pune",
            "chilakaluripet"
        ]

        for loc in locations:

            if loc in q:
                location = loc.title()
                break


        # ----------------------------------------------
        # STATUS
        # ----------------------------------------------

        if "absent" in q:

            status = "Absent"

        elif "inactive" in q:

            status = "Inactive"

        elif "active" in q:

            status = "Active"


        # ----------------------------------------------
        # DEPARTMENT
        # ----------------------------------------------

        departments = [
            "engineering",
            "hr",
            "finance",
            "marketing",
            "sales",
            "operations",
            "it"
        ]

        for dept in departments:

            if dept in q:
                department = dept.title()
                break


        # ----------------------------------------------
        # RETURN STRUCTURED ROUTE
        # ----------------------------------------------

        return {
            "strategy": "structured_rag",
            "employee_id": employee_id,
            "department": department,
            "location": location,
            "status": status
        }


    # ==================================================
    # STEP 4: LLM FALLBACK
    # ==================================================

    prompt = f"""
You are a router for an employee AI assistant.

Choose exactly ONE strategy.

structured_rag:
Simple employee data from SQLite.

graph_rag:
Employee relationships, managers, reporting, connections.

live_rag:
Current weather or other live external information.

Return ONLY valid JSON.

USER QUESTION:
{question}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a strict JSON router."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(
            f"Router returned invalid JSON: {content}"
        )

    strategy = result.get("strategy")

    if strategy not in VALID_STRATEGIES:
        raise ValueError(
            f"Invalid strategy: {strategy}"
        )

    return result


# --------------------------------------------------
# EXECUTE ROUTED QUERY
# --------------------------------------------------

def answer_query(question):

    route = route_question(question)

    print("\nROUTER RESULT")
    print("-------------------------")
    print(route)

    strategy = route["strategy"]


    # ----------------------------------------------
    # STRUCTURED RAG
    # ----------------------------------------------

    if strategy == "structured_rag":

        from structured_rag import structured_rag_query

        return structured_rag_query(
            question=question,
            employee_id=route.get("employee_id"),
            department=route.get("department"),
            location=route.get("location"),
            status=route.get("status")
        )


    # ----------------------------------------------
    # GRAPH RAG
    # ----------------------------------------------

    if strategy == "graph_rag":

        from graph_rag import graph_rag_query

        employee_name = route.get("employee_name")

        if not employee_name:

            return "I couldn't identify the employee in your question."

        return graph_rag_query(
            question,
            employee_name
        )


    # ----------------------------------------------
    # LIVE RAG
    # ----------------------------------------------

    if strategy == "live_rag":

        from live_rag import live_rag_query

        city = route.get("city")

        if not city:

            return "I couldn't identify the city in your question."

        return live_rag_query(
            question=question,
            city=city
        )


    raise ValueError(
        f"Unsupported strategy: {strategy}"
    )


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    question = (
        "can you give me list of names "
        "who are absent in the bangalore location"
    )

    print("\nQUESTION")
    print("-------------------------")
    print(question)

    result = route_question(question)

    print("\nROUTER RESULT")
    print("-------------------------")
    print(result)
