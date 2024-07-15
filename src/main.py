from resource_manager import is_master


if is_master():
    from main_master import main
    main()
else:
    from main_slave import main
    main()