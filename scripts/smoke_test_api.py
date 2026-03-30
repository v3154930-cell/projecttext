"""
Smoke test for API scenarios.
Uses only stdlib: subprocess, time, json, urllib, re, sys, os.
"""

import subprocess
import sys
import time
import json
import urllib.request
import urllib.error
import re
import os

BASE_URL = "http://127.0.0.1:8001"
passed = 0
failed = 0
results = []


def log_result(test_name, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        status = "PASS"
    else:
        failed += 1
        status = "FAIL"
    results.append((status, test_name, detail))
    print(f"  [{status}] {test_name}" + (f" -- {detail}" if detail else ""))


def post(path, body):
    url = BASE_URL + path
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {body_text}")


def get(path):
    url = BASE_URL + path
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {body_text}")


def reset_session(sid):
    """Reset a session to ensure clean state."""
    try:
        post(f"/api/session/{sid}/reset", {})
    except Exception:
        pass


def wait_for_server(url, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=3) as resp:
                return True
        except Exception:
            time.sleep(0.5)
    return False


def find_unfilled_placeholders(text):
    """Find {xxx} placeholders that were not substituted."""
    single_brace = re.findall(r'\{[a-z_]+\}', text)
    return list(single_brace)


def run_scenario_steps(scenario_type, session_id, steps):
    """Run a sequence of steps for a scenario, return (success, final_response, error)."""
    reset_session(session_id)
    # Init step: send empty answer to move from START to first question
    init_r = post(f"/api/scenario/{scenario_type}", {"session_id": session_id, "answer": ""})
    if init_r.get("question") in (None, ""):
        return False, init_r, "init step returned no question"
    for i, (answer, label) in enumerate(steps):
        r = post(f"/api/scenario/{scenario_type}", {"session_id": session_id, "answer": answer})
        if i < len(steps) - 1:
            if r.get("is_complete"):
                return False, r, f"premature is_complete=true after {label}"
            if r.get("question") in (None, ""):
                return False, r, f"no question after {label}"
        else:
            return True, r, None
    return True, None, None


# =========================================================================
# Start server
# =========================================================================
print("=" * 60)
print("Starting uvicorn on port 8001...")
print("=" * 60)

# Kill anything on port 8001 first
try:
    subprocess.run(
        ["powershell", "-Command",
         "Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue | "
         "ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"],
        capture_output=True, timeout=10
    )
    time.sleep(2)
except Exception:
    pass

server_proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8001"],
    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

final_doc_simple = None
final_doc_adv = None
final_doc_loan = None

try:
    if not wait_for_server(BASE_URL + "/docs"):
        print("FATAL: Server did not start in time")
        sys.exit(1)

    print("Server is ready.\n")

    # =====================================================================
    # A. Basic start contract
    # =====================================================================
    print("--- A. Basic start contract ---")

    for stype in ["receipt_simple", "receipt_advanced", "loan"]:
        sid = f"test-a-{stype}"
        reset_session(sid)
        try:
            r = post(f"/api/scenario/{stype}", {"session_id": sid, "answer": ""})
            ok = (
                r.get("question") not in (None, "")
                and r.get("is_complete") == False
                and r.get("document") is None
                and r.get("error") is None
            )
            detail = "" if ok else f"resp={json.dumps(r, ensure_ascii=False)}"
            log_result(f"A: {stype} start contract", ok, detail)
        except Exception as e:
            log_result(f"A: {stype} start contract", False, str(e))
        reset_session(sid)

    # =====================================================================
    # B. Happy path receipt_simple
    # =====================================================================
    print("\n--- B. Happy path receipt_simple ---")
    steps_rs = [
        ("Ivanov Ivan Ivanovich", "receiver FIO"),
        ("4510 123456, UVD g. Moskvy, 01.01.2020", "passport"),
        ("Petrov Petr Petrovich", "sender FIO"),
        ("100000", "amount"),
        ("01.01.2025", "date"),
        ("25.12.2026", "return_date"),
        ("Moskva", "city"),
    ]
    try:
        ok, r, err = run_scenario_steps("receipt_simple", "test-b-rs", steps_rs)
        if ok and r:
            final_doc_simple = r.get("document")
            doc_ok = (
                r.get("is_complete") == True
                and r.get("document") not in (None, "")
                and r.get("current_step") == "done"
            )
            detail = "" if doc_ok else f"resp={json.dumps(r, ensure_ascii=False)[:300]}"
            log_result(f"B: city -> is_complete=true", doc_ok, detail)
        elif err:
            log_result(f"B: happy path", False, err)
    except Exception as e:
        log_result(f"B: happy path", False, str(e))

    # =====================================================================
    # C. Happy path receipt_advanced (with optional fields)
    # =====================================================================
    print("\n--- C. Happy path receipt_advanced ---")
    steps_adv = [
        ("Ivanov Ivan Ivanovich", "receiver FIO"),
        ("4510 123456, UVD g. Moskvy, 01.01.2020", "passport"),
        ("Petrov Petr Petrovich", "sender FIO"),
        ("50000", "amount"),
        ("01.01.2025", "date"),
        ("25.12.2026", "return_date"),
        ("Moskva", "city"),
        ("10% godovyh", "interest_rate"),
        ("s dnya polucheniya do dnya vozvrata", "interest_period"),
        ("0.1% ot summy za kazhdyj den'", "penalty"),
        ("nalichnymi", "repayment_order"),
    ]
    try:
        ok, r, err = run_scenario_steps("receipt_advanced", "test-c-ra", steps_adv)
        if ok and r:
            final_doc_adv = r.get("document")
            doc_ok = (
                r.get("is_complete") == True
                and r.get("document") not in (None, "")
            )
            detail = "" if doc_ok else f"resp={json.dumps(r, ensure_ascii=False)[:300]}"
            log_result(f"C: final -> is_complete=true", doc_ok, detail)
        elif err:
            log_result(f"C: happy path", False, err)
    except Exception as e:
        log_result(f"C: happy path", False, str(e))

    # =====================================================================
    # D. Happy path loan (with repayment_method)
    # =====================================================================
    print("\n--- D. Happy path loan ---")
    steps_loan = [
        ("Ivanov Ivan Ivanovich", "lender"),
        ("Petrov Petr Petrovich", "borrower"),
        ("500000", "amount"),
        ("01.01.2025", "date"),
        ("25.12.2026", "term"),
        ("10% godovyh", "interest_rate"),
        ("po chastam ezhemesyachno", "repayment_method"),
        ("Moskva", "city"),
        ("prvoobretanie nedvizhimosti", "purpose"),
        ("0.1% ot summy za kazhdyj den'", "penalty"),
        ("zalog kvartiry", "collateral"),
    ]
    try:
        ok, r, err = run_scenario_steps("loan", "test-d-loan", steps_loan)
        if ok and r:
            final_doc_loan = r.get("document")
            doc_ok = (
                r.get("is_complete") == True
                and r.get("document") not in (None, "")
            )
            detail = "" if doc_ok else f"resp={json.dumps(r, ensure_ascii=False)[:300]}"
            log_result(f"D: final -> is_complete=true", doc_ok, detail)
            # Check repayment_method in document
            if final_doc_loan and "po chastam ezhemesyachno" in final_doc_loan:
                log_result(f"D: document contains repayment_method", True)
            elif final_doc_loan:
                log_result(f"D: document contains repayment_method", False,
                           "repayment_method text not found in document")
            else:
                log_result(f"D: document contains repayment_method", False, "document is None/empty")
        elif err:
            log_result(f"D: happy path", False, err)
    except Exception as e:
        log_result(f"D: happy path", False, str(e))

    # =====================================================================
    # E. Placeholder check
    # =====================================================================
    print("\n--- E. Placeholder check ---")
    for name, doc in [("receipt_simple", final_doc_simple),
                       ("receipt_advanced", final_doc_adv),
                       ("loan", final_doc_loan)]:
        if doc is None:
            log_result(f"E: {name} has document", False, "document is None")
            continue
        issues = find_unfilled_placeholders(doc)
        if issues:
            log_result(f"E: {name} no unfilled placeholders", False, f"found: {issues[:5]}")
        else:
            log_result(f"E: {name} no unfilled placeholders", True)

    # =====================================================================
    # F. Validation scenarios
    # =====================================================================
    print("\n--- F. Validation scenarios ---")

    # F1: receipt_simple - empty receiver FIO
    sid = "test-f1-rs"
    reset_session(sid)
    try:
        post(f"/api/scenario/receipt_simple", {"session_id": sid, "answer": ""})
        r2 = post(f"/api/scenario/receipt_simple", {"session_id": sid, "answer": ""})
        ok = (
            r2.get("is_complete") == False
            and r2.get("document") is None
            and r2.get("question") is not None
        )
        detail = "" if ok else f"resp={json.dumps(r2, ensure_ascii=False)[:200]}"
        log_result("F1: receipt_simple empty FIO validation", ok, detail)
    except Exception as e:
        log_result("F1: receipt_simple empty FIO validation", False, str(e))

    # F2: receipt_advanced - empty passport
    sid = "test-f2-ra"
    reset_session(sid)
    try:
        post(f"/api/scenario/receipt_advanced", {"session_id": sid, "answer": ""})
        post(f"/api/scenario/receipt_advanced", {"session_id": sid, "answer": "Test FIO"})
        r = post(f"/api/scenario/receipt_advanced", {"session_id": sid, "answer": ""})
        ok = (
            r.get("is_complete") == False
            and r.get("document") is None
            and r.get("question") is not None
        )
        detail = "" if ok else f"resp={json.dumps(r, ensure_ascii=False)[:200]}"
        log_result("F2: receipt_advanced empty passport validation", ok, detail)
    except Exception as e:
        log_result("F2: receipt_advanced empty passport validation", False, str(e))

    # F3: loan - non-numeric amount
    sid = "test-f3-loan"
    reset_session(sid)
    try:
        post(f"/api/scenario/loan", {"session_id": sid, "answer": ""})
        post(f"/api/scenario/loan", {"session_id": sid, "answer": "Test Lender"})
        post(f"/api/scenario/loan", {"session_id": sid, "answer": "Test Borrower"})
        r = post(f"/api/scenario/loan", {"session_id": sid, "answer": "abc"})
        ok = (
            r.get("is_complete") == False
            and r.get("document") is None
            and r.get("question") is not None
        )
        detail = "" if ok else f"resp={json.dumps(r, ensure_ascii=False)[:200]}"
        log_result("F3: loan non-numeric amount validation", ok, detail)
    except Exception as e:
        log_result("F3: loan non-numeric amount validation", False, str(e))

    # =====================================================================
    # G. Reset / Status
    # =====================================================================
    print("\n--- G. Reset / Status ---")
    sid = "test-g-session"
    reset_session(sid)
    try:
        post(f"/api/scenario/receipt_simple", {"session_id": sid, "answer": "Test"})
        status = get(f"/api/session/{sid}/status")
        has_scenario = "receipt_simple" in status.get("scenarios", {})
        log_result("G1: status shows active scenario", has_scenario,
                   "" if has_scenario else f"status={json.dumps(status)}")
    except Exception as e:
        log_result("G1: status shows active scenario", False, str(e))

    try:
        reset_resp = post(f"/api/session/{sid}/reset", {})
        log_result("G2: reset returns ok", reset_resp.get("status") == "ok",
                   "" if reset_resp.get("status") == "ok" else str(reset_resp))
        status2 = get(f"/api/session/{sid}/status")
        is_not_found = status2.get("status") == "not_found"
        is_empty = len(status2.get("scenarios", {})) == 0
        ok = is_not_found or is_empty
        log_result("G3: status after reset is empty/not_found", ok,
                   "" if ok else f"status={json.dumps(status2)}")
    except Exception as e:
        log_result("G2/G3: reset/status", False, str(e))

    # =====================================================================
    # H. claim_simple
    # =====================================================================
    print("\n--- H. claim_simple ---")
    try:
        r = post(f"/api/scenario/claim_simple", {"session_id": "test-h", "answer": ""})
        ok = r.get("error") is not None
        detail = "" if ok else f"resp={json.dumps(r, ensure_ascii=False)}"
        log_result("H: claim_simple returns error", ok, detail)
    except Exception as e:
        log_result("H: claim_simple returns error", False, str(e))

    # =====================================================================
    # I. Legacy endpoints
    # =====================================================================
    print("\n--- I. Legacy endpoints ---")
    for stype in ["receipt_simple", "receipt_advanced"]:
        sid = f"test-i-{stype}"
        reset_session(sid)
        try:
            r = post(f"/api/scenario/{stype}", {"session_id": sid, "answer": ""})
            ok = r.get("question") not in (None, "")
            detail = "" if ok else f"resp={json.dumps(r, ensure_ascii=False)}"
            log_result(f"I: legacy /api/scenario/{stype}", ok, detail)
        except Exception as e:
            log_result(f"I: legacy /api/scenario/{stype}", False, str(e))

    # =====================================================================
    # Summary
    # =====================================================================
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed, {passed + failed} total")
    print("=" * 60)

    if failed > 0:
        print("\nFailed tests:")
        for status, name, detail in results:
            if status == "FAIL":
                print(f"  FAIL: {name}" + (f" -- {detail}" if detail else ""))
        print()
        sys.exit(1)
    else:
        print("\nAll tests passed!")

finally:
    print("\nStopping server...")
    server_proc.terminate()
    try:
        server_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_proc.kill()
        server_proc.wait()
    print("Server stopped.")
