from checker import (
    build_url,
    is_https,
    show_response,
    check_site,
    scan_sites,
    check_headers,
    retry_check,
)


def main():
    print("\n=== Partea 1: Funcții ===")
    print("build_url 1:", build_url("example.com", "login"))
    print("build_url 2:", build_url("example.com", "/login"))
    print("is_https 1:", is_https("https://example.com"))
    print("is_https 2:", is_https("http://example.com"))

    print("\n=== Partea 2: Cerere GET ===")
    # show_response își afișează singură rezultatul.
    try:
        show_response("https://example.com")
    except Exception as error:
        print("show_response nu a reușit:", error)
    try:
        show_response("https://httpbin.org/status/404")
    except Exception as error:
        print("show_response pentru cazul-limită nu a reușit:", error)

    print("\n=== Partea 3: Verificarea unui site ===")
    print("Site funcțional:", check_site("https://example.com"))
    print("Site inexistent:", check_site("http://this-site-does-not-exist.invalid"))

    print("\n=== Partea 4: Scanarea tuturor site-urilor ===")
    scan_sites()

    print("\n=== Partea 5: Antete de securitate ===")
    print(
        "Cu două antete custom:",
        check_headers(
            "https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff"
        ),
    )
    print("Fără antete custom:", check_headers("https://httpbin.org/json"))

    print("\n=== Partea 6: Încercări repetate ===")
    print("Status 404 (se oprește după prima încercare):",
          retry_check("https://httpbin.org/status/404"))
    print("Status 500 (reîncearcă de două ori):",
          retry_check("https://httpbin.org/status/500", attempts=2))


if __name__ == "__main__":
    main()
