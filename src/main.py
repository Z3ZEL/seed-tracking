from args import is_main

def build_server():
    from server import app
    return app


if is_main():
    from main_main import main
    main()
else:
    from main_worker import main
    main()