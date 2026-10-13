import requests

# Adresele date în fișierul de pornire. Nu adăugăm alte adrese aici.
SITES = [
    # Pagini obișnuite (Părțile 2, 3 și 4)
    "https://example.com",
    "https://httpbin.org/html",
    "https://httpbin.org/json",
    "https://httpbin.org/status/200",
    "https://httpbin.org/redirect/1",
    "https://httpbin.org/delay/2",
    # Pagini care eșuează
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/10",
    "http://this-site-does-not-exist.invalid",
    # Anteturi de securitate (Partea 5)
    "https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff",
    "https://httpbin.org/response-headers?x-frame-options=DENY",
    # Răspunde aleatoriu cu 200 sau 500 (Partea 6)
    "https://httpbin.org/status/200,500",
]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
]


def build_url(host, path):
    """Returnează o adresă completă, indiferent dacă path începe cu /."""
    return "https://" + host.strip("/") + "/" + path.strip("/")


def is_https(url):
    """Returnează True dacă adresa folosește HTTPS."""
    return url.lower().startswith("https://")


def show_response(url):
    """Trimite un GET și afișează statusul și Content-Type."""
    response = requests.get(url, timeout=5)
    print("Status:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type", "unknown"))


def check_site(url):
    """Returnează informații despre site; nu lasă erorile de rețea să oprească programul."""
    try:
        response = requests.get(url, timeout=5)
        content_type = response.headers.get("Content-Type", "unknown").split(";")[0].strip()
        return {
            "status": response.status_code,
            "content_type": content_type,
            "length": len(response.content),
            "server": response.headers.get("Server", "unknown"),
        }
    except requests.RequestException as error:
        return {"status": None, "error": str(error)[:120]}


def scan_sites():
    """Verifică toate site-urile, afișează răspunsurile 200 și un rezumat."""
    results = []
    for url in SITES:
        results.append((url, check_site(url)))

    successful = [(url, result) for url, result in results if result.get("status") == 200]
    failed = [(url, result) for url, result in results if result.get("status") != 200]

    successful.sort(key=lambda item: item[1].get("length", 0), reverse=True)

    print("Site-uri funcționale (status 200), sortate după mărime:")
    for url, result in successful:
        print(f"{url} -> 200, {result.get('length', 0)} octeți")

    print(f"Reușite: {len(successful)} | Eșuate: {len(failed)}")


def check_headers(url):
    """Verifică prezența antetelor de securitate și calculează scorul."""
    try:
        response = requests.get(url, timeout=5)
        # HTTP headers nu țin cont de majuscule/minuscule.
        received_headers = {name.lower() for name in response.headers.keys()}
        present = [name for name in SECURITY_HEADERS if name.lower() in received_headers]
        missing = [name for name in SECURITY_HEADERS if name.lower() not in received_headers]
        score = int(len(present) / len(SECURITY_HEADERS) * 100)
        return {"present": present, "missing": missing, "score": score}
    except requests.RequestException as error:
        return {"status": None, "error": str(error)[:120]}


def retry_check(url, attempts=3):
    """Reîncearcă pentru erori de conexiune sau status 5xx."""
    attempts = max(1, int(attempts))
    actual_attempts = 0
    last_status = None
    last_error = None

    for _ in range(attempts):
        actual_attempts += 1
        try:
            response = requests.get(url, timeout=5)
            last_status = response.status_code
            last_error = None

            # Status sub 500 (inclusiv 4xx): nu mai încercăm.
            if response.status_code < 500:
                return {"status": last_status, "attempts": actual_attempts}
        except requests.RequestException as error:
            # Păstrăm ultimul status HTTP primit, dacă a existat unul.
            last_error = str(error)[:120]

    result = {"status": last_status, "attempts": actual_attempts}
    if last_error is not None and last_status is None:
        result["error"] = last_error
    return result
