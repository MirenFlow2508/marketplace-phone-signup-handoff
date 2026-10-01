import argparse

from src.marketplace_signup import InfraiClient, SignupRequest, complete_signup


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a marketplace seller session")
    parser.add_argument("phone")
    parser.add_argument("code")
    parser.add_argument("name")
    parser.add_argument("seller_asset")
    args = parser.parse_args()
    result = complete_signup(InfraiClient(), SignupRequest(args.phone, args.code, args.name, args.seller_asset))
    print(f"seller {result.user_id} can hand off {result.asset} with session {result.session_id}")


if __name__ == "__main__":
    main()
