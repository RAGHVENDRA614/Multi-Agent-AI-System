from backend.agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)


def main():
    print("=" * 60)
    print("        ResearchMind - Multi Agent System")
    print("=" * 60)

    topic = input("\nEnter Research Topic: ").strip()

    if not topic:
        print("Please enter a valid topic.")
        return

    # ---------------- Search Agent ----------------
    print("\n🔍 Search Agent is working...")

    search_agent = build_search_agent()

    search_response = search_agent.invoke(
        {
            "messages": [
                (
                    "user",
                    f"Find recent, reliable and detailed information about: {topic}",
                )
            ]
        }
    )

    search_result = search_response["messages"][-1].content

    print("✅ Search Completed.")

    # ---------------- Reader Agent ----------------
    print("\n📄 Reader Agent is working...")

    reader_agent = build_reader_agent()

    reader_response = reader_agent.invoke(
        {
            "messages": [
                (
                    "user",
                    f"""
Based on the following search results about '{topic}',
pick the most relevant URL and scrape it for deeper content.

Search Results:

{search_result[:800]}
""",
                )
            ]
        }
    )

    reader_result = reader_response["messages"][-1].content

    print("✅ Scraping Completed.")

    # ---------------- Writer ----------------
    print("\n✍️ Writing Research Report...")

    research = f"""
SEARCH RESULTS

{search_result}


DETAILED SCRAPED CONTENT

{reader_result}
"""

    report = writer_chain.invoke(
        {
            "topic": topic,
            "research": research,
        }
    )

    print("✅ Report Generated.")

    # ---------------- Critic ----------------
    print("\n🧐 Critic Reviewing Report...")

    feedback = critic_chain.invoke(
        {
            "report": report,
        }
    )

    print("✅ Review Completed.")

    # ---------------- Output ----------------
    print("\n" + "=" * 80)
    print("FINAL RESEARCH REPORT")
    print("=" * 80)
    print(report)

    print("\n" + "=" * 80)
    print("CRITIC FEEDBACK")
    print("=" * 80)
    print(feedback)

    # ---------------- Save Report ----------------
    filename = topic.replace(" ", "_") + "_report.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📁 Report saved as: {filename}")


if __name__ == "__main__":
    main()