from args import is_master

def build_server():
    from server import app
    return app


if is_master():
    from main_master import main
    main()
else:
    from main_slave import main
    main()