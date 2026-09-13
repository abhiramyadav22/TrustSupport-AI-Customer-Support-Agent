"""Interactive CLI demonstration of TrustSupport AI agent with structured explainability."""

import json
import os
import sys
import pickle
from typing import Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.pipeline.agent import TrustSupportAgent
from src.schema import RoutingDecision


def load_agent(
    model_path: str = "data/sample/models/calibrated_intent.pkl",
    index_path: str = "data/sample/models/historical_index.pkl",
) -> TrustSupportAgent:
    if not os.path.exists(model_path) or not os.path.exists(index_path):
        print("Error: Trained model or index not found. Please run 'python scripts/train_intent.py' first.")
        sys.exit(1)

    with open(model_path, "rb") as f:
        classifier = pickle.load(f)
    with open(index_path, "rb") as f:
        retrieval_index = pickle.load(f)

    return TrustSupportAgent(
        classifier=classifier,
        retrieval_index=retrieval_index,
        brand_name="AmazonHelp",
    )


def print_agent_output(output):
    print("\n" + "=" * 80)
    print(f"CUSTOMER MESSAGE: \"{output.customer_message}\"")
    print("-" * 80)
    print(f"PREDICTED INTENT:     {output.intent.upper()}")
    print(f"INTENT CONFIDENCE:    {output.intent_confidence:.1%}")
    print(f"ROUTING DECISION:     {output.decision.value}")
    print(f"COMPOSITE RISK SCORE: {output.risk_score:.2f}")

    if output.risk_flags:
        print(f"RISK FLAGS TRIGGERED: {', '.join(output.risk_flags)}")
    else:
        print("RISK FLAGS TRIGGERED: None (Clean routing)")

    print(f"\nDECISION RATIONALE:\n  -> {output.escalation_reason}")

    print("\nRETRIEVED HISTORICAL EVIDENCE PRECEDENTS:")
    if output.retrieved_evidence:
        for idx, ev in enumerate(output.retrieved_evidence, 1):
            print(f"  [{idx}] Case ID: {ev.case_id} | Similarity: {ev.similarity_score:.3f} | Action: {ev.resolution_action}")
            print(f"      Historical Problem: \"{ev.customer_problem[:80]}...\"")
            print(f"      Historical Reply:   \"{ev.historical_reply[:90]}...\"")
    else:
        print("  (No high-confidence historical evidence retrieved)")

    print(f"\nPROPOSED DRAFT REPLY:\n  \"{output.reply}\"")
    print("=" * 80 + "\n")


def interactive_mode():
    agent = load_agent()
    print("=" * 80)
    print("TrustSupport AI - Grounded Support Agent Interactive CLI")
    print("Brand: AmazonHelp | Model: Calibrated Intent + Historical Grounding Engine")
    print("Type a customer support message to test the agent, or type 'quit' / 'exit' to stop.")
    print("=" * 80)

    sample_queries = [
        "Where is my package? It was supposed to be delivered yesterday and tracking hasn't updated.",
        "The box arrived today but the screen is completely cracked and broken.",
        "I need to cancel order #402-9812 immediately before it ships out.",
        "My credit card was charged $450 from your site and I never authorized this! My card was stolen!",
        "I am contacting my attorney tomorrow morning and suing you for breach of contract.",
    ]

    print("\nQuick test queries:")
    for idx, q in enumerate(sample_queries, 1):
        print(f"  {idx}. {q}")
    print()

    while True:
        try:
            user_input = input("Customer Message (or 1-5 for preset, 'q' to quit) > ").strip()
            if not user_input or user_input.lower() in ["quit", "exit", "q"]:
                print("Exiting CLI demo.")
                break

            if user_input in ["1", "2", "3", "4", "5"]:
                user_input = sample_queries[int(user_input) - 1]

            output = agent.process_message(user_input)
            print_agent_output(output)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting CLI demo.")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        agent = load_agent()
        out = agent.process_message(query)
        print_agent_output(out)
    else:
        interactive_mode()
