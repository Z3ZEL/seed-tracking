from args import is_main
### Route the main function to the right file


if is_main():
    from main_main import main
    main()
else:
    from main_worker import main
    main()