from app.agent.graph import run_turn


def chat(sid, msg):
    r = run_turn(sid, msg)
    print("\nUSER:", msg)
    print("BOT :", r["answer"])
    print(f"[category={r.get('category')} priority={r.get('priority')} "
          f"status={r.get('status')} tools={[a['tool'] for a in r.get('action_log', [])]}]")


print("\n##### 1. VPN issue, user says resolved")
chat("s1", "My VPN is not connecting")
chat("s1", "yes, resolved")

print("\n##### 2. Password reset (tool action)")
chat("s2", "I forgot my password")

print("\n##### 3. Security incident (auto escalate)")
chat("s3", "I clicked a phishing link in an email")

print("\n##### 4. Printer issue, still not fixed (escalate)")
chat("s4", "printer shows offline and jobs are stuck")
chat("s4", "no, still not working")