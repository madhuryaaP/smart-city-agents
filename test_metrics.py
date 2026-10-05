import requests
import time
import json
import sys

API_URL = "https://smart-city-agents.onrender.com/ask"
TIMEOUT = 120
DELAY = 5  # seconds between requests to avoid Groq rate limits

def call_api(question):
    """Call API with retry on failure."""
    for attempt in range(2):
        try:
            start = time.time()
            resp = requests.post(
                API_URL,
                json={"question": question},
                timeout=TIMEOUT
            )
            elapsed = time.time() - start
            data = resp.json()
            return data, elapsed
        except Exception as e:
            print(f"    Attempt {attempt+1} failed: {e}")
            if attempt == 0:
                time.sleep(10)
    return None, 0


def detect_agents(data):
    """Detect which agents returned data."""
    routed = []
    if not data:
        return routed

    # Planner: check if planner dict has keys beyond empty
    p = data.get("planner", {})
    if p and isinstance(p, dict) and len(p) > 0:
        routed.append("planner")

    # Traffic
    t = data.get("traffic", {})
    if t and isinstance(t, dict) and len(t) > 0:
        routed.append("traffic")

    # Water
    w = data.get("water", {})
    if w and isinstance(w, dict) and len(w) > 0:
        routed.append("water")

    # Pollution
    pol = data.get("pollution", {})
    if pol and isinstance(pol, dict) and len(pol) > 0:
        routed.append("pollution")

    # Infrastructure
    inf = data.get("infrastructure", {})
    if inf and isinstance(inf, dict) and len(inf) > 0:
        routed.append("infrastructure")

    return routed


# ============================================================
# 5.1 — AGENT ROUTING ACCURACY
# ============================================================

routing_tests = [
    # Planner (5)
    {"query": "Plan my day from LB Nagar to Hitech City", "expected": "planner"},
    {"query": "I need to reach Gachibowli from Kukatpally by 9 AM", "expected": "planner"},
    {"query": "Plan my trip from Ameerpet to HITEC City", "expected": "planner"},
    {"query": "How do I reach Secunderabad from LB Nagar by 10 AM", "expected": "planner"},
    {"query": "Plan my journey from Dilsukhnagar to Madhapur", "expected": "planner"},
    # Traffic (5)
    {"query": "How is traffic in Kothapet", "expected": "traffic"},
    {"query": "Traffic conditions from LB Nagar to Hitech City", "expected": "traffic"},
    {"query": "Is there congestion in Ameerpet right now", "expected": "traffic"},
    {"query": "Road traffic in Madhapur", "expected": "traffic"},
    {"query": "Check traffic on Jubilee Hills road", "expected": "traffic"},
    # Water (5)
    {"query": "What is the weather in Hyderabad today", "expected": "water"},
    {"query": "Is it going to rain in LB Nagar", "expected": "water"},
    {"query": "Temperature in Kukatpally", "expected": "water"},
    {"query": "Humidity and rainfall in Secunderabad", "expected": "water"},
    {"query": "Is there any flood risk in Dilsukhnagar", "expected": "water"},
    # Pollution (5)
    {"query": "What is the air quality in Hyderabad", "expected": "pollution"},
    {"query": "AQI in Kukatpally area", "expected": "pollution"},
    {"query": "Is the air safe in Gachibowli today", "expected": "pollution"},
    {"query": "Pollution level near Charminar", "expected": "pollution"},
    {"query": "PM2.5 levels in Ameerpet", "expected": "pollution"},
    # Infrastructure (5)
    {"query": "Are there potholes in Madhapur", "expected": "infrastructure"},
    {"query": "Broken streetlights near Kukatpally", "expected": "infrastructure"},
    {"query": "Road damage in LB Nagar", "expected": "infrastructure"},
    {"query": "Civic problems reported in Kondapur", "expected": "infrastructure"},
    {"query": "Infrastructure issues in Banjara Hills", "expected": "infrastructure"},
]


def test_routing_accuracy():
    print("="*60)
    print("5.1 — AGENT ROUTING ACCURACY")
    print("="*60)
    sys.stdout.flush()

    results = {"planner": {"total": 0, "correct": 0},
               "traffic": {"total": 0, "correct": 0},
               "water": {"total": 0, "correct": 0},
               "pollution": {"total": 0, "correct": 0},
               "infrastructure": {"total": 0, "correct": 0}}

    for i, test in enumerate(routing_tests):
        query = test["query"]
        expected = test["expected"]
        results[expected]["total"] += 1

        data, elapsed = call_api(query)

        if data:
            routed = detect_agents(data)
            correct = expected in routed
            if correct:
                results[expected]["correct"] += 1

            status = "OK" if correct else "MISS"
            print(f"  [{status}] '{query}'")
            print(f"         expected={expected}, got={routed}, time={elapsed:.1f}s")
        else:
            print(f"  [ERR] '{query}'")

        sys.stdout.flush()
        if i < len(routing_tests) - 1:
            time.sleep(DELAY)

    print("\n" + "-"*60)
    print(f"{'Agent':<18} {'Test Queries':>12} {'Correct':>10} {'Accuracy':>10}")
    print("-"*60)
    total_q = 0
    total_c = 0
    for agent in ["planner", "traffic", "water", "pollution", "infrastructure"]:
        t = results[agent]["total"]
        c = results[agent]["correct"]
        acc = (c / t * 100) if t > 0 else 0
        print(f"{agent.capitalize():<18} {t:>12} {c:>10} {acc:>9.0f}%")
        total_q += t
        total_c += c
    overall = (total_c / total_q * 100) if total_q > 0 else 0
    print("-"*60)
    print(f"{'Overall':<18} {total_q:>12} {total_c:>10} {overall:>9.0f}%")
    print()
    sys.stdout.flush()
    return results


# ============================================================
# 5.2 — RESPONSE TIME ANALYSIS
# ============================================================

response_time_tests = {
    "Traffic": [
        "How is traffic in Kothapet",
        "Traffic from LB Nagar to Hitech City",
        "Road congestion in Madhapur",
    ],
    "Water": [
        "What is the weather in Hyderabad",
        "Is it raining in LB Nagar",
        "Temperature in Kukatpally today",
    ],
    "Pollution": [
        "Air quality in Hyderabad",
        "AQI in Kukatpally",
        "PM2.5 levels in Ameerpet",
    ],
    "Infrastructure": [
        "Potholes in Madhapur",
        "Road damage reports in LB Nagar",
        "Broken streetlights in Kukatpally",
    ],
    "Planner": [
        "Plan my trip from LB Nagar to Hitech City",
        "I need to reach Gachibowli from Kukatpally by 9 AM",
        "Plan my day from Ameerpet to Madhapur",
    ],
    "Multi-Agent Planning": [
        "Plan my day from LB Nagar to HITEC City, also check pollution and weather",
        "I need to reach Gachibowli by 10 AM from LB Nagar, check traffic and air quality",
        "Plan my trip from Dilsukhnagar to Kukatpally with weather and pollution info",
    ],
}


def test_response_times():
    print("="*60)
    print("5.2 — RESPONSE TIME ANALYSIS")
    print("="*60)
    sys.stdout.flush()

    results = {}
    for qtype, queries in response_time_tests.items():
        times = []
        for q in queries:
            data, elapsed = call_api(q)
            if data:
                times.append(elapsed)
                print(f"  [{qtype}] '{q}' — {elapsed:.2f}s")
            else:
                print(f"  [{qtype}] '{q}' — ERROR")
            sys.stdout.flush()
            time.sleep(DELAY)

        if times:
            results[qtype] = sum(times) / len(times)
        else:
            results[qtype] = None

    print("\n" + "-"*50)
    print(f"{'Query Type':<25} {'Avg Response Time (s)':>20}")
    print("-"*50)
    for qtype in ["Traffic", "Water", "Pollution", "Infrastructure", "Planner", "Multi-Agent Planning"]:
        avg = results.get(qtype)
        if avg is not None:
            print(f"{qtype:<25} {avg:>20.2f}")
        else:
            print(f"{qtype:<25} {'ERROR':>20}")
    print()
    sys.stdout.flush()
    return results


# ============================================================
# 5.3 — RAG RETRIEVAL PERFORMANCE
# ============================================================

pollution_rag_queries = [
    "What are the main sources of air pollution in Hyderabad",
    "How does industrial pollution affect Hyderabad",
    "What steps is Hyderabad taking to reduce pollution",
    "PM2.5 health effects in Hyderabad",
    "Vehicular emissions in Hyderabad city",
    "Air pollution trends in Telangana",
    "Pollution control measures in Hyderabad",
    "What causes smog in Hyderabad",
    "Pollution near construction sites in Hyderabad",
    "How bad is air quality in winter in Hyderabad",
]

infra_rag_queries = [
    "What are the major infrastructure problems in Hyderabad",
    "Pothole issues on Hyderabad roads",
    "Streetlight maintenance in Hyderabad",
    "Road repair status in Hyderabad",
    "Smart city infrastructure projects in Hyderabad",
    "Drainage problems in Hyderabad",
    "Public transport infrastructure in Hyderabad",
    "Water supply infrastructure issues",
    "Civic problems reported by citizens",
    "Hyderabad road quality assessment",
]


def test_rag_performance():
    print("="*60)
    print("5.3 — RAG RETRIEVAL PERFORMANCE")
    print("="*60)
    sys.stdout.flush()

    poll_relevant = 0
    poll_total = len(pollution_rag_queries)
    poll_scores = []
    poll_chunks = []

    print("\n--- Pollution Agent RAG ---")
    for q in pollution_rag_queries:
        data, elapsed = call_api(q)
        if data:
            pollution_data = data.get("pollution", {})
            rag = pollution_data.get("rag", {})
            context = rag.get("context", [])
            found = rag.get("found", False)

            if found and context:
                poll_relevant += 1
                poll_chunks.append(len(context))
                distances = [c.get("distance", 1.0) for c in context]
                scores = [round(1 - d, 4) for d in distances]
                avg_score = sum(scores) / len(scores) if scores else 0
                poll_scores.append(avg_score)
                print(f"  [FOUND] '{q}' — {len(context)} chunks, avg_score={avg_score:.4f}")
            else:
                # Check if live_data had info even if RAG didn't
                live = pollution_data.get("live_data", {})
                if live.get("available"):
                    print(f"  [LIVE]  '{q}' — live AQI data (no RAG chunks)")
                else:
                    print(f"  [MISS]  '{q}' — no relevant chunks")
        else:
            print(f"  [ERR]   '{q}'")
        sys.stdout.flush()
        time.sleep(DELAY)

    infra_relevant = 0
    infra_total = len(infra_rag_queries)
    infra_scores = []
    infra_chunks = []

    print("\n--- Infrastructure Agent RAG ---")
    for q in infra_rag_queries:
        data, elapsed = call_api(q)
        if data:
            infra_data = data.get("infrastructure", {})
            rag_sub = infra_data.get("rag", {})
            if rag_sub:
                context = rag_sub.get("context", [])
                found = rag_sub.get("found", False)
            else:
                context = infra_data.get("context", [])
                found = infra_data.get("found", False)

            if found and context:
                infra_relevant += 1
                infra_chunks.append(len(context))
                distances = [c.get("distance", 1.0) for c in context]
                scores = [round(1 - d, 4) for d in distances]
                avg_score = sum(scores) / len(scores) if scores else 0
                infra_scores.append(avg_score)
                print(f"  [FOUND] '{q}' — {len(context)} chunks, avg_score={avg_score:.4f}")
            else:
                print(f"  [MISS]  '{q}' — no relevant chunks")
        else:
            print(f"  [ERR]   '{q}'")
        sys.stdout.flush()
        time.sleep(DELAY)

    # Summary
    print("\n" + "-"*65)
    print(f"{'RAG Metric':<30} {'Pollution':>15} {'Infrastructure':>15}")
    print("-"*65)

    col_count = collection_count()
    print(f"{'Knowledge chunks in DB':<30} {col_count:>15} {col_count:>15}")
    print(f"{'Queries tested':<30} {poll_total:>15} {infra_total:>15}")
    print(f"{'Queries with relevant chunks':<30} {poll_relevant:>15} {infra_relevant:>15}")

    avg_poll_chunks = sum(poll_chunks)/len(poll_chunks) if poll_chunks else 0
    avg_infra_chunks = sum(infra_chunks)/len(infra_chunks) if infra_chunks else 0
    print(f"{'Avg chunks retrieved':<30} {avg_poll_chunks:>15.1f} {avg_infra_chunks:>15.1f}")

    poll_avg = sum(poll_scores)/len(poll_scores) if poll_scores else 0
    infra_avg = sum(infra_scores)/len(infra_scores) if infra_scores else 0
    print(f"{'Avg relevance score':<30} {poll_avg:>15.4f} {infra_avg:>15.4f}")

    poll_acc = (poll_relevant / poll_total * 100) if poll_total else 0
    infra_acc = (infra_relevant / infra_total * 100) if infra_total else 0
    print(f"{'Retrieval accuracy':<30} {poll_acc:>14.0f}% {infra_acc:>14.0f}%")
    print()
    sys.stdout.flush()
    return {
        "poll_relevant": poll_relevant, "poll_total": poll_total,
        "poll_avg_score": poll_avg, "poll_avg_chunks": avg_poll_chunks,
        "infra_relevant": infra_relevant, "infra_total": infra_total,
        "infra_avg_score": infra_avg, "infra_avg_chunks": avg_infra_chunks,
    }


def collection_count():
    """Estimate knowledge chunk count from known DB state."""
    return 367


# ============================================================
# RUN ALL TESTS
# ============================================================

if __name__ == "__main__":
    print("\nChecking if API is reachable...")
    sys.stdout.flush()
    try:
        r = requests.get(
            "https://smart-city-agents.onrender.com/",
            timeout=120
        )
        print(f"API status: {r.status_code}\n")
    except Exception as e:
        print(f"API unreachable: {e}")
        print("Make sure the server is deployed and running.")
        exit(1)

    sys.stdout.flush()

    # Run specific section if given as argument
    section = sys.argv[1] if len(sys.argv) > 1 else "all"

    if section in ("all", "routing", "1"):
        test_routing_accuracy()

    if section in ("all", "time", "2"):
        test_response_times()

    if section in ("all", "rag", "3"):
        test_rag_performance()

    print("\n" + "="*60)
    print("ALL TESTS COMPLETE")
    print("="*60)
